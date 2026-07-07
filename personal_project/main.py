# fastapi 입력
from fastapi import FastAPI
from pydantic import BaseModel

from personal_project.baseline import rag_chain
from personal_project.graph import graph

app = FastAPI(title="강의자료 검색")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer : str

@app.get("/")
def root():
  return {"status" : "ok", "message" : "connect"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    result = graph.invoke({"question" : req.question})
    return AskResponse(answer=result['answer']) #그래프 전체값을 반환해버리므로 answer 만 추출하여준다

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

