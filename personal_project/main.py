# fastapi 입력
import os
import tempfile
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from personal_project import baseline
from langgraph.types import Command
from personal_project.graph_chapter import graph_chapter

host = os.environ.get("HOST")

load_dotenv()

app = FastAPI(title="강의자료 검색")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[host],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    v = result["__interrupt__"][0].value
    if "__interrupt__" in result:
        return AskResponse(status="interrupted", thread_id=thread_id,
                           stage=v.get("stage"), msg=v.get("msg"),
                           answer=(v.get("answer") or result.get("answer")))
    return AskResponse(status="completed", thread_id=thread_id,
                       answer=(v.get("answer") or result.get("answer")))

@app.get("/")
def root():
  return {"status" : "ok", "message" : "connect"}

@app.post("/upload")
def upload(file : UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_fath = tmp.name
    try:
        baseline.build_vectorstore(tmp_fath)
    finally:
        os.remove(tmp_fath)
    return {"filename": file.filename}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    result = graph_chapter.invoke({"cont" : req.question},
                          config = {"configurable" : {"thread_id" : thread_id}})

    return build_response(result, thread_id)

@app.post("/resume", response_model=AskResponse)
def resume(req : ResumeRequest):
    thread_id = req.thread_id
    result = graph_chapter.invoke(Command(resume = req.reply),
                          config = {"configurable" : {"thread_id" : thread_id}})
    response = build_response(result, thread_id)
    print("=== resume 응답:", response)  # ← 이 줄 추가

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

