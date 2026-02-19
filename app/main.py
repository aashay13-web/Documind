from fastapi import FastAPI
from pydantic import BaseModel

# Make the project root importable when running this file as a script
import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

# Use absolute import so both `python app/main.py` and Uvicorn work
from app.retrieval import answer_question

app = FastAPI(title="DocuMind Enterprise - RAG API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

@app.post("/query", response_model=QueryResponse)
async def query_rag(req: QueryRequest):
    result = answer_question(req.question)
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
    )
