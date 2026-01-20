from fastapi import APIRouter, HTTPException,Depends
from app.db.model import Booking
from qdrant_client import QdrantClient
from pydantic import BaseModel
from app.services.embeddings import emddeding  
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from app.db.redis import redis_client
import numpy as np
from ollama import AsyncClient
from app.services.dataextraction import extract_booking_details
from app.db.sql import SessionLocal
from sqlalchemy.orm import Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv("api.env")
router = APIRouter(prefix="/chat", tags=["Chat"])
q_client = QdrantClient("http://localhost:6333")


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_user"






@router.post("/ask")
async def chat_with_pdf(request: ChatRequest,db: Session = Depends(get_db)):
    try:
        query = request.query
        session_id = request.session_id
        raw_history = redis_client.lrange(f"chat:{session_id}", 0, 9)
        chat_history = [json.loads(m) for m in reversed(raw_history)]
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
        history_interview_list = redis_client.lrange(f"chat:{session_id}", -3, -1)
        history_interview = "\n".join([json.loads(m)['content'] for m in history_interview_list])
        query_vector = np.array(emddeding(query)).tolist()
        
        search_results = q_client.query_points(
            collection_name="RAG",
            query=query_vector,
            limit=3
        )
               

        
        context_text = ""
        if search_results and search_results.points:
           context_text = "\n\n".join([
                                         res.payload.get("text", "") 
                                 for res in search_results.points  
                                            ])
        else:
            context_text = "No relevant context found in PDFs."

        
        prompt = f"""
        [SYSTEM INSTRUCTION]
        You are a professional HR Assistant. 
        TASK 1: Answer questions using ONLY the [CONTEXT].
        TASK 2: Booking interviews. To book an interview, you ONLY need: Name, Email, Date, and Time. 
        ***IMPORTANT***: Do NOT ask for a Room ID or any other information not listed above.!
        ***IMPORTANT***: DO not reply \n\nBest Regards,\nHR Assistant [University, Kathmandu]\n\n✅.
        while booking interview don0t response from content o

        [CONTEXT]
        {context_text}

        [HISTORY]
        {history_text}

        [USER QUERY]
        {query}
        """

        
        response = await AsyncClient().chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
        ai_answer = response['message']['content']

        has_intent = any(word in query.lower() for word in ["booking", "interview"])
        was_booking_active = any(word in history_interview.lower() for word in ["booking", "interview"])

        if has_intent or was_booking_active:
            full_conversation = history_text + "\nUser: " + query 
            details = extract_booking_details(full_conversation)
            

            
            if all([details.get("name"), details.get("email"), details.get("date"), details.get("time")]):
                try:
                    new_booking = Booking(
                        candidate_name=details["name"],
                        candidate_email=details["email"],
                        interview_date=details["date"],
                        interview_time=details["time"]
                    )
                    db.add(new_booking)
                    db.commit()
                    db.refresh(new_booking)
                    ai_answer += "\n\n✅ Your interview has been successfully recorded in our database."
                except Exception as sql_err:
                    db.rollback()
                    print(f"SQL Error: {sql_err}")

        
        user_msg = {"role": "User", "content": query}
        ai_msg = {"role": "Assistant", "content": ai_answer}
        redis_client.lpush(f"chat:{session_id}", json.dumps(user_msg), json.dumps(ai_msg))
        redis_client.expire(f"chat:{session_id}", 86400)

        return {
            "answer": ai_answer,
            "sources": list(set([res.payload.get("filename", "Unknown") for res in search_results.points]))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))