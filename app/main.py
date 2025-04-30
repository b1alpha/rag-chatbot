from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag_pipeline import get_answer

app = FastAPI()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/query")
async def query(request: QueryRequest):
    try:
        answer = get_answer(request.question)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
