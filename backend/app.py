from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "backend running"}

@app.post("/query")
def query(data: QueryRequest):
    return {"received_question": data.question}
