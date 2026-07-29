# fastapi 입력
import uuid
from fastapi import FastAPI
from pydantic import BaseModel

from personal_project.graph import graph
from langgraph.types import Command

app = FastAPI(title="강의자료 검색")

class AskRequest(BaseModel):
    question: str
    thread_id : str | None = None

class AskResponse(BaseModel):
    answer : str | None = None
    status : str
    thread_id : str
    stage : str | None = None
    msg : str | None = None

class ResumeRequest(BaseModel):
    thread_id : str
    reply : str

def build_response(result, thread_id) -> AskResponse:
    if "__interrupt__" in result:
        v = result["__interrupt__"][0].value
        return  AskResponse(status="interrupted", thread_id=thread_id,
                            stage=v["stage"], msg=v["msg"])
    return AskResponse(status="completed", thread_id=thread_id,
                       answer=result["answer"])

@app.get("/")
def root():
  return {"status" : "ok", "message" : "connect"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    result = graph.invoke({"question" : req.question},
                          config = {"configurable" : {"thread_id" : thread_id}})

    #인터럽트 부분
    #따옴표 넣을곳 안넣을곳 구분하자!!
    if "__interrupt__" in result:
        return AskResponse(status = "interrupted", thread_id=thread_id, question = result['__interrupt__'][0].value)

    return AskResponse(status="completed", answer=result['answer'], thread_id= thread_id) #완료

@app.post("/resume", response_model=AskResponse)
def resume(req : ResumeRequest):
    thread_id = req.thread_id
    result = graph.invoke(Command(resume = req.interrupt_answer),
                          config = {"configurable" : {"thread_id" : thread_id}})

    return AskResponse(status="completed", thread_id= thread_id, answer=result['answer'])




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

