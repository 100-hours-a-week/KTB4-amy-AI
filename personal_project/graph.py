# 랭그래프 마이그레이션
#import
from langchain_community.tools import vectorstore
from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import List
from langchain_core.documents import Document
from personal_project.baseline import retriever, prompt, llm

class MyState(TypedDict): #typeddict == 형식지정
  question : str
  context : List[Document]
  answer : str
  search_query : str
  retry_count : int
  similarity_average : float

#점수 꺼내서 메타 데이터에 넣기
def search(state: MyState) -> dict:
  res = vectorstore.similarity_search_with_score(state['search_query'], k=3)
  doc_list = []
  for doc, score in res:
    doc.metadata['score'] = score
    doc_list.append(doc)
  return {"context" : doc_list} # 질문을 통해 적합한 내용 추출
  #similarity 메서드를 통해 자동으로 rag 이 들어가기 때문에 반환값 retriever.invoke에서 지금으로 변환하여준다

def learn(state: MyState) -> dict:
  learn_chain = (prompt | llm | StrOutputParser()) # 기존 랭체인은 생성과 검색 기능이 함께 있었기에 생성용 랭체인 선언
  return {"answer" : learn_chain.invoke({"context": state['context'], "question": state['question']})} #내용을 프롬프트에 넣어서 적합한 정답 추출

def initialize(state : MyState) -> dict:
  search_query = state['question']
  retry_count = 0
  return {"search_query" : search_query, "retry_count" : retry_count}

#점수 평균 내기
def evaluate(state : MyState) -> dict:
  tmp = state['context']
  num = 0
  for doc in tmp:
    num += doc.metadata['score']
  similarity_average = num / len(tmp)
  return {"similarity_average" : similarity_average}

#시도 횟수 세주기, search_query 내용 바꿔주기(최대 시도 횟수 제한 및 재검색 용)
def research(state : MyState) -> dict:
  return {"retry_count" : state['retry_count'] + 1}


#그래프 구상
builder = StateGraph(MyState)
builder.add_node("search", search)
builder.add_node("learn", learn)
builder.add_node("initialize", initialize)
builder.add_edge(START, "initialize")
builder.add_edge("initialize", "search")
builder.add_edge("search", "learn")
builder.add_edge("learn", END)

graph = builder.compile(checkpointer=MemorySaver())
result = graph.invoke({"question": "니체의 핵심이론은?", "answer": ""})
print(result)