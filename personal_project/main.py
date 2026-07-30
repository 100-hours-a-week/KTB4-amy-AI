# fastapi 입력
import uuid
from fastapi import FastAPI
from pydantic import BaseModel

from personal_project.graph import graph
from langgraph.types import Command

from personal_project.graph_chapter import graph_chapter

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
        v = result["__interrupt__"][0].value #보통 결과가 복수일것을 생각해서 리스트로 받아오나 여기선 단일이므로 0번째 값을 받아옴
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
    result = graph_chapter.invoke({"question" : req.question},
                          config = {"configurable" : {"thread_id" : thread_id}})

    #인터럽트 부분
    #따옴표 넣을곳 안넣을곳 구분하자!!
    return build_response(result, thread_id)

@app.post("/resume", response_model=AskResponse)
def resume(req : ResumeRequest):
    thread_id = req.thread_id
    result = graph_chapter.invoke(Command(resume = req.reply),
                          config = {"configurable" : {"thread_id" : thread_id}})

    return build_response(result, thread_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

