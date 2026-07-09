# 랭그래프 마이그레이션
#import
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from typing_extensions import TypedDict
from typing import List
from langchain_core.documents import Document
from personal_project.baseline import retriever, prompt, llm, vectorstore
from personal_project.prompt import prompt_replace


class MyState(TypedDict): #typeddict == 형식지정
  question : str
  context : List[Document]
  answer : str
  search_query : str
  retry_count : int
  similarity_average : float
  check : str

#초기화
def initialize(state : MyState) -> dict:
  search_query = state['question']
  retry_count = 0
  search_state = 0
  return {"search_query" : search_query, "retry_count" : retry_count, "search_state" : search_state}

#점수 꺼내서 메타 데이터에 넣기
def search(state: MyState) -> dict:
  print(state['search_query'])
  res = vectorstore.similarity_search_with_score(state['search_query'], k=3)
  doc_list = []
  for doc, score in res:
    doc.metadata['score'] = score
    doc_list.append(doc)
  return {"context" : doc_list} # 질문을 통해 적합한 내용 추출
  #similarity 메서드를 통해 자동으로 rag 이 들어가기 때문에 반환값 retriever.invoke에서 지금으로 변환하여준다

#점수 평균 내기
def evaluate(state : MyState) -> dict:
  tmp = state['context']
  num = 0
  for doc in tmp:
    num += doc.metadata['score']
  similarity_average = num / len(tmp)
  print(similarity_average)
  return {"similarity_average" : similarity_average}

#분기 - 오류 여부 판단
def router(state : MyState) -> str:
  print(state['retry_count'])
  if state['retry_count'] < 2 and state['similarity_average'] >= 0.3: # 아미친 거리인거 까먹지 말기!!! 부등호 방향 반대될뻔...
    if state['retry_count'] == 0:
      return "ask"
    else:
      return "retry"
  elif state['retry_count'] >= 2:
    return "fail"
  else:
    return "learn"

def ask(state : MyState) -> dict:
  tmp = interrupt("문서에서 내용을 찾을 수 없습니다. 웹 검색으로 전환할까요? (네/아니요)")
  if "아니요" in tmp:
    check = "doc"
  else:
    check = "web"
  return {"check" : check}

def ask_router(state : MyState) -> str:
  print(state['check'])
  if state['check'] == 'doc':
    return "retry"
  else:
    return "web_search"

def web_search(state : MyState) -> dict:


#시도 횟수 세주기, search_query 내용 바꿔주기(최대 시도 횟수 제한 및 재검색 용)
def retry(state : MyState) -> dict:
  make_answer_chain = (prompt_replace | llm | StrOutputParser())
  tmp = []
  for doc in state['context']:
    tmp.append(doc.page_content)
  res = "\n\n".join(tmp)
  #res = "\n\n".join(doc.page_content for doc in state['context']), 컴프리헨션 써서 간략화한 코드 대괄호를 빼는경우 제네레이터가 되므로 바로바로 join 시킬 수 있어 리스트화 해서 넘겨주는것보다 효율적
  return {"retry_count" : state['retry_count'] + 1, "search_query" : make_answer_chain.invoke({"result" : res, "question" : state['question'], "search_query" : state['search_query']})}

#들어온 문서 프롬프트에 맞게 가공해서 answer 에 보내주기
def learn(state: MyState) -> dict:
  learn_chain = (prompt | llm | StrOutputParser()) # 기존 랭체인은 생성과 검색 기능이 함께 있었기에 생성용 랭체인 선언
  return {"answer" : learn_chain.invoke({"context": state['context'], "question": state['question']})} #내용을 프롬프트에 넣어서 적합한 정답 추출

def fail(state : MyState) -> dict:
  return {"answer" : "문서에서 찾을 수 없습니다"}

#그래프 구상
builder = StateGraph(MyState)
builder.add_node("search", search)
builder.add_node("learn", learn)
builder.add_node("initialize", initialize)
builder.add_node("retry", retry)
builder.add_node("evaluate", evaluate)
builder.add_node("fail", fail)

builder.add_edge(START, "initialize")
builder.add_edge("initialize", "search")
builder.add_edge("search", "evaluate")
builder.add_conditional_edges(
  "evaluate",
  router,
  {"retry" : "retry", "learn" : "learn", "fail" : "fail"},
)
builder.add_edge("retry", "search")
builder.add_edge("learn", END)
builder.add_edge("fail", END)

graph = builder.compile()
result = graph.invoke({"question": "랭그래프가 뭐야", "answer": ""})
print(result)