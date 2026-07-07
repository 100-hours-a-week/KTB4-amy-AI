# fastapi 입력
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="강의자료 검색")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.get("/")
def root():
  return {"status" : "ok", "message" : "connect"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    answer = rag_chain.invoke(req.question)
    return AskResponse(answer=answer)

