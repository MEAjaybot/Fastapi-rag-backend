import re 
from fastapi import APIRouter,Form
from typing import List,Literal
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 



def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunks_fixed(text:str,chunk_size= 50,overlap=0.1)-> List[str]:
    text_word = clean_text(text)
    overlap_int = int(chunk_size*overlap)
    chunks =[]
    for i in range(0,len(text_word),chunk_size-overlap_int):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
    

    return chunks

def recursive_chunk_with_langchain(documents: str, max_chunk_size:1000, overlap: int = 100) -> List[str]:

    doc = Document(page_content=documents, metadata={})
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    
    
    chunked_texts = splitter.split_text(doc.page_content)
    return chunked_texts    

def chunk_text_service(text: str, strategy: str = "fixed") -> List[str]:
    text = clean_text(text)  # your existing text cleaning

    if strategy == "fixed":
        return chunks_fixed(text)
    else:
        return recursive_chunk_with_langchain(text)



