from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.retrieval import stream_answer

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
@limiter.limit("5/minute")
def query_rag(request: Request, req: QueryRequest):
    return StreamingResponse(stream_answer(req.question), media_type="text/event-stream")