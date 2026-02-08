from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "backend running"}

@app.post("/query")
def query():
    return {"message": "Query endpoint wired"}
