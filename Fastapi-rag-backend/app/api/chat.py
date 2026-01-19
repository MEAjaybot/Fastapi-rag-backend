from fastapi import APIRouter, HTTPException,Depends
from app.db.model import Booking# Your existing Qdrant client
from qdrant_client import QdrantClient
from pydantic import BaseModel
from app.services.embeddings import emddeding  # Your embedding model function
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

# 2. Request Model for POST
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_user"

# Configure Gemini (Replace with your actual key)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
MODEL_NAME = "models/gemini-3-flash-preview" 
llm_model = genai.GenerativeModel(MODEL_NAME)



@router.post("/ask")
async def chat_with_pdf(request: ChatRequest,db: Session = Depends(get_db)):
    try:
        query = request.query
        session_id = request.session_id
        raw_history = redis_client.lrange(f"chat:{session_id}", 0, 9)
        chat_history = [json.loads(m) for m in reversed(raw_history)]
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
        
        query_vector = np.array(emddeding(query)).tolist()
        # 2. Search Qdrant for top 3 matching chunks
        search_results = q_client.query_points(
            collection_name="RAG",
            query=query_vector,
            limit=3
        )
               

        # 3. Create context from the hits
        context_text = ""
        if search_results and search_results.points:
           context_text = "\n\n".join([
                                         res.payload.get("text", "") 
                                 for res in search_results.points  # Access the .points list
                                            ])
        else:
            context_text = "No relevant context found in PDFs."

        
        prompt = f"""
        [SYSTEM INSTRUCTION]
        You are a professional HR Assistant. 
        TASK 1: Answer questions using ONLY the [CONTEXT].
        TASK 2: Booking interviews. To book an interview, you ONLY need: Name, Email, Date, and Time. 
        ***IMPORTANT***: Do NOT ask for a Room ID or any other information not listed above.!
        \n\nBest Regards,\nHR Assistant [University, Kathmandu]\n\n✅.

        [CONTEXT]
        {context_text}

        [HISTORY]
        {history_text}

        [USER QUERY]
        {query}
        """

        # 4. Generate AI Answer
        response = await AsyncClient().chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
        ai_answer = response['message']['content']

        # 5. DATA EXTRACTION & POSTGRES SAVING
        # We check the current query + history to see if we finally have a full booking
        full_conversation = history_text + "\nUser: " + query 
        details = extract_booking_details(full_conversation)
        print(f"DEBUG: Extracted Details -> {details}")

        # Ensure all required fields are present before saving
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

        # 6. Save to Redis (Maintain History)
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