#문서로딩, 인덱싱 등 그래프 데이터 전처리 및 프롬프트 입력

import os
#환경변수 받아오기
EMBEDDED = os.environ.get("EMBEDED")
FILEPATH = os.environ.get("FILEPATH")
CHUNK_SIZE = os.environ.get("CHUNK_SIZE")
CHUNK_OVERLAP = os.environ.get("CHUNK_OVERLAP")
DB = os.environ.get("DB")
TOP_K = os.environ.get("TOP_K")

#import
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate #프롬프트용
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser  #파서용
from langchain_core.runnables import RunnablePassthrough
from langsmith import Client
from langsmith.evaluation import evaluate

#fastapi 래핑
from fastapi import FastAPI
from pydantic import BaseModel
import nest_asyncio
import uvicorn

#임베딩 - 구글 api 소모 속도가 생각보다 빨라서 임시로 허깅 페이스 사용 중
#FIXME : 구글 임베딩으로 변경하기
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDED,
    encode_kwargs={"prompt": "passage: ", "normalize_embeddings": True},
    query_encode_kwargs={"prompt": "query: ", "normalize_embeddings": True},
)

#문서 로드 및 청킹
all_docs = []
for path in FILEPATH:
    loader = PyMuPDFLoader(path)
    all_docs.extend(loader.load())   # 페이지별 Document 리스트. metadata에 page 포함

splitter = RecursiveCharacterTextSplitter(
    chunk_size = CHUNK_SIZE,
    chunk_overlap = CHUNK_OVERLAP,
)
chunks = splitter.split_documents(all_docs)

print(f"{chunks[0].page_content[:80]}...")

#db
#NOTE : db가 없을때만 생성되도록

if (os.path.exists(DB)) != True:
  vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB,
  )
  print("인덱싱 완료. Chroma 저장 위치:", DB)

else:
  print("이미 chroma db 가 존재합니다")

#체인
#HACK : 왜인지는 모르겠는데 llm이 성공적으로 호출되어도 계속 호출하는 현상이 있어서 최대 호출횟수 지정해서 해결 하였음
#NOTE : 아니 근데 출력 결과 너무 맘에 안드는데 맘에 드는 결과 나올때까지 작성하자니 프롬프트 너무 길어질것 같고
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 교육자 입니다. 주어진 문서에 근거하여 질문에 답해주세요\n"
     "당신의 최우선 사항은 사용자의 이해입니다.\n"
     "사용자의 질문이 문제풀이와 같은 정답을 요구하는것일 경우 정답을 절대로 알려주어선 안됩니다. 정답쪽으로 유도하여야 합니다.\n"
     "사용자가 내용을 이해됐다 파악되면 설명한 개념에 대한 요약을 해주세요. 새롭게 익힌것, 헷갈린것들 위주로 작성해야합니다.\n"
     "자료에 없는 내용 일 경우 자료에서 찾을 수 없습니다 라고 대답합니다.\n"
     "설명이 끝난 이후에는 사용자가 내용을 파악했는지 내용에 점검하는 과정을 가지세요 설명은 사용자가 이해할때까지 계속되어야 합니다\n"
     ),
    ("human",
     "문서 : {context}\n\n"
     "질문 : {question}"
     )
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)