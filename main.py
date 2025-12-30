from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

try:
    rag_bot = SBLRAG(debug=False)
    print("✅ RAG Engine Initialized Successfully")
except Exception as e:
    print(f"❌ Failed to initialize RAG Engine: {e}")
    rag_bot = None

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"status": "online", "message": "Science-Based Lifting Chatbot is Ready"}

@app.post("/chat")
def chat(request: QueryRequest):
    if not rag_bot:
        raise HTTPException(status_code=500, detail="RAG Engine not initialized")
    
    try:
        result = rag_bot.ask(request.query)
        
        # Return answer and sources for the frontend to display
        sources = list(set([doc.metadata.get('source', 'Unknown') for doc in result['context']]))
        
        return {
            "answer": result["answer"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)