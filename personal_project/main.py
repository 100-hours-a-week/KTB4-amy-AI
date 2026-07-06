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

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#테스트
test_q = "니체가 말하는 삶이 뭐야?"
print("Q:", test_q)
print("A:", rag_chain.invoke(test_q))

#실패 테스트
test_q = "전통적 세계해석에 대한 비판이 뭐야?"
print("Q:", test_q)
print("A:", rag_chain.invoke(test_q))

def contains_expected_keyword(run, example):
    pred = run.outputs.get("answer", "")
    expected = example.outputs.get("answer", "")

    keywords = [w for w in expected.split() if len(w) >= 2][:2]
    hit = all(k in pred for k in keywords)

    return {
        "key": "contains_expected_keyword",
        "score": 1 if hit else 0,
        "comment": f"필수 키워드 {keywords} 포함 여부",
    }

#데이터셋 생성
assert "rag_chain" in dir(), "rag_chain이 존재하지 않습니다"
assert "llm" in dir(), "llm이 존재하지 않습니다"


client = Client()

DATASET_NAME = "personal-project-eval"

existing = [d for d in client.list_datasets(dataset_name = DATASET_NAME)]

if existing:
  dataset = existing[0]
else:
  dataset = client.create_dataset(
      dataset_name = DATASET_NAME,
      description = 'rag 품질 평가용'
  )

print(dataset.id)

#example 추가
client.create_examples(
    dataset_id = dataset.id,
    inputs = [
        {"question" : "관점주의란"},
        {"question" : "주황색"},
        {"question" : "니체가 말하는 삶이 뭐야?"},
    ],
    outputs = [
        {"answer" : '''관점주의는 진리가 다양한 관점들의 충돌과 해석의 산물이라고 보며, 모든 관점이 동등한 가치를 갖지 않고 삶에 더 봉사하는 관점이 우월하다고 주장합니다. 이는 관점들의 끊임없는 충돌과 경쟁이라는 역동적인 과정에 주목하며, 더 높은 수준의 창조적이고 삶을 긍정하는 관점이 그렇지 않은 관점을 극복한다고 봅니다. 관점주의는 모든 해석을 의심하고 새로운 가치를 창조하려는 적극적인 태도를 요구하며, '보다 나은 관점'을 향해 나아가는 것을 목표로 합니다.

또한 관점주의에서 '나'라는 주체는 고정된 실체가 아닌 다양한 힘과 충동의 역동적 결합체이며, 새로운 관점을 창조함으로써 삶을 확장하고 강화하려는 '힘에의 의지'와 연결된 능동적인 행위입니다. 주관주의와 달리, 관점은 한 개인의 의식이나 마음의 산물이 아니라 생명체로서 '몸', 곧 특정 생명체가 처한 생리학적, 심리적 조건이 세계를 해석하는 방식을 의미합니다. 따라서 관점주의는 절대적 진리를 부정하고 다양한 관점의 존재를 긍정하며, 삶을 긍정하고 새롭게 창조하기 위한 해석을 시도하고 삶에 봉사하는 새로운 가치의 창조를 추구합니다.'''},
        {"answer" : "자료에서 찾을 수 없습니다"},
        {"answer" : '''제시된 문서에 따르면, 니체가 말하는 삶은 다음과 같은 특징을 가집니다.

첫째, 삶은 **스스로 경험 상황을 구성하고 창조하는 과정**입니다. 그는 자신의 삶을 위한 관점적 경험 상황을 스스로 만들고, 그 상황에 의미와 가치를 부여함으로써 모든 순간이 자신에게 의미 있고 필연적임을 아는 자입니다.

둘째, 이러한 삶은 **고통의 영원한 회귀를 확고히 의지하는 것**을 포함합니다. 이는 고통을 더 이상 정당화할 필요 없이 받아들이고 긍정하는 태도를 의미합니다.

셋째, 그는 **자신의 힘을 확신하고 인간이 도달한 힘에 긍지를 가지는 자**입니다. 이는 자기 자신과 인간의 잠재력에 대한 강한 믿음과 자부심을 나타냅니다.

요약하자면, 니체에게 삶은 **미학적(창조적) 해석을 통한 디오니소스적 자기긍정의 삶**입니다. 이는 자신의 삶을 예술 작품처럼 창조하고, 그 안에서 고통까지도 긍정하며, 자신의 힘과 가치를 확신하는 삶을 의미합니다.

제가 설명해 드린 내용이 니체가 말하는 삶의 개념을 이해하는 데 도움이 되셨을까요? 혹시 더 궁금하거나 헷갈리는 부분이 있으신가요?'''},
    ]
)

examples = list(client.list_examples(dataset_name = DATASET_NAME))

#평가 작동 확인용 - example의 question 값을 넣어 실제 답변 생성
def target(inputs):
  return {"answer" : rag_chain.invoke(inputs["question"])}

#평가용 랭체인
JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 답변 품질을 평가하는 채점자입니다.\n"
     "아래 기대 답변(reference)과 모델 답변 (prediction)을 비교하고,\n"
     "의미가 일치하면 1, 부분적으로만 일치하면 0.5, 무관하면 0을 점수로 매기세요.\n"
     "점수를 출력할때에는 무조건 숫자로만 출력하도록 하세요"),
    ("human",
     "질문 : {question}\n\n"
     "기대 답변: {reference}\n\n"
     "모델 답변 : {prediction}"),

])

eval_chain = JUDGE_PROMPT | llm | StrOutputParser()

def llm_eval(run, example):
  reply = eval_chain.invoke({
      "question" : example.inputs["question"],
      "reference" : example.outputs["answer"],
      "prediction" : run.outputs["answer"],
  })

  first_line = reply.strip().splitlines()[0].strip()
  try:
    score = float(first_line)
  except ValueError:
    score = 0
  return{
      "key": "llm_judge_semantic_match",
      "score": score,
      "comment": reply,
  }

result = evaluate(
    target, #인보크 돌리기용
    data = DATASET_NAME, #데이터셋
    evaluators = [contains_expected_keyword, llm_eval], #평가함수
    experiment_prefix = "v1-baseline" #평가 결과지 앞에 붙이는 이름
)

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

ngrok.set_auth_token(userdata.get("ngrok_token"))
ngrok.kill()
public_url = ngrok.connect(8000)
print("공용 URL:", public_url)
print("문서(Swagger):", f"{public_url}/docs")

config = uvicorn.Config(app, host = "0.0.0.0", port=8000)
server = uvicorn.Server(config)
await server.serve()

# 랭그래프 마이그레이션
#import

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import List
from langchain_core.documents import Document

class MyState(TypedDict): #typeddict == 형식지정
  question : str
  context : List[Document]
  answer : str

def search(state: MyState) -> dict:
  return {"context" : retriever.invoke(state['question'])}

def learn(state: MyState) -> dict:
  learn_chain = (prompt | llm | parser)
  return {"answer" : learn_chain.invoke({"context": state['context'], "question": state['question']})}

#그래프 구상

builder = StateGraph(MyState)
builder.add_node("in", increment)
builder.add_node("gr", greet)
builder.add_edge(START, "in")
builder.add_edge("in", "gr")
builder.add_edge("gr", END)

graph = builder.compile()
result = graph.invoke({"count": 0, "message": ""})
print(result)