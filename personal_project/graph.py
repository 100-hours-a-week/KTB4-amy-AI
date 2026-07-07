# 랭그래프 마이그레이션
#import
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

def search(state: MyState) -> dict:
  return {"context" : retriever.invoke(state['question'])} # 질문을 통해 적합한 내용 추출

def learn(state: MyState) -> dict:
  learn_chain = (prompt | llm | StrOutputParser()) # 기존 랭체인은 생성과 검색 기능이 함께 있었기에 생성용 랭체인 선언
  return {"answer" : learn_chain.invoke({"context": state['context'], "question": state['question']})} #내용을 프롬프트에 넣어서 적합한 정답 추출

#그래프 구상
builder = StateGraph(MyState)
builder.add_node("search", search)
builder.add_node("learn", learn)
builder.add_edge(START, "search")
builder.add_edge("search", "learn")
builder.add_edge("learn", END)

graph = builder.compile(checkpointer=MemorySaver())
result = graph.invoke({"question": "니체의 핵심이론은?", "answer": ""})
print(result)