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