import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
# We import SBLRAG, but we won't use it immediately
from rag_engine import SBLRAG
import uvicorn

app = FastAPI(title="SBL Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_bot = None

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    history: List[Message] = []

@app.get("/")
def home():
    return {"status": "online", "message": "Science-Based Lifting Chatbot is Ready"}

@app.post("/chat")
def chat(request: QueryRequest):
    # Lazy loading
    global rag_bot
    if rag_bot is None:
        print(" Loading RAG Engine for the first time... (This may take 10-20 seconds)")
        try:
            rag_bot = SBLRAG(debug=True)
            print("RAG Engine Loaded!")
        except Exception as e:
            print(f"Failed to load brain: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize AI Brain")
    
    # Normal processing
    try:
        history_data = [msg.dict() for msg in request.history]
        result = rag_bot.ask(request.query, history=history_data)
        
        sources = list(set([doc.metadata.get('source', 'Unknown') for doc in result['context']]))
        
        return {
            "answer": result["answer"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Dynamic port
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Server on Port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)