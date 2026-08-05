import os
import sqlite3

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from personal_project import baseline
TOP_K = int(os.environ.get("TOP_K"))
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel
from typing_extensions import TypedDict
from personal_project.baseline import llm
from personal_project.classifiers import classify_unclear, to_yn
from personal_project.graph import builder as qa_builder
from personal_project.prompt import chapter_prompt, lecture_prompt, clarify_prompt

class Index(BaseModel):
    parent_index : int
    chapter_index : int

class ChapterState(TypedDict):
    question: str
    parent_index : int
    chapter_index : int
    text : list
    answer : str
    cont : str
    cursor : int
    check_state : str

#llm 만들어주기
model_key = os.environ.get("claude_api_key")
model_name = os.environ.get("MODEL_C")

lecture_llm = ChatAnthropic(model=model_name, api_key=model_key, max_retries=0)
lecture_chain = (lecture_prompt | lecture_llm | StrOutputParser())
clarify_chain = clarify_prompt | llm | StrOutputParser()

def format_with_index(docs):
    return "\n\n".join(
        f"[parent_index={d.metadata['parent_index']}, chapter_index = {d.metadata['chapter_index']}]{d.page_content}"
        for d in docs
    )

def returnChapter(state : ChapterState):
    retriever = baseline.vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    chapter_structure = llm.with_structured_output(Index)
    chapter_chain = ( {'context' : retriever | format_with_index, 'question' : RunnablePassthrough()}
            | chapter_prompt | chapter_structure)
    result = chapter_chain.invoke(state['question'])
    return {'parent_index' : result.parent_index, 'chapter_index' : result.chapter_index}

def textChapter(state : ChapterState):
    #1안 벡터 검색으로 고치기
    #2안 받는건 챕터별로 받되 출력만 쪼개서 하기(스크리닝?)
    pr = state['parent_index']
    ch = state['chapter_index']
    print(f"=== textChapter 조회: parent_index={pr}, chapter_index={ch}")

    tmp = baseline.vectorstore.get(where={"$and" : [ #연산자 시퀄문용 $ == chroma 연산자
        {"parent_index" : pr},
        {"chapter_index" : ch},
    ]})

    items = list(zip(tmp['documents'], tmp['metadatas'])) #rawdata를 page_content, metadata 형식으로 묶어주기
    items.sort(key = lambda x : x[1]['chunk_index'])
    context = " ".join(c for c,m in items) #순서에 맞춰 청킹된 텍스트들 합쳐주기

    #챕터 통째로 랭체인에 넣어주기
    answer = lecture_chain.invoke({'context' : context})
    result = [p.strip() for p in answer.split('---') if p.strip()]

    return {'text' : result, 'cursor' : 0}

def printChapter(state : ChapterState):
    answer = state['text'][state['cursor']]
    return {'answer' : answer}

def ask(state : ChapterState):
    reply = interrupt({"stage" : "yn", "msg" : "이어서 다음 내용을 설명할까요? (Y/N)"})
    return {'cont' : reply}

def nextChunk(state : ChapterState):
    return {'cursor' : state['cursor'] + 1}

def nextChapter(state : ChapterState):
    p = state['parent_index']
    c = state['chapter_index']

    if c < baseline.chapter_count[p]:
        return {'chapter_index' : c + 1}
    else:
        return {'parent_index' : p + 1, 'chapter_index' : 1}

def toQA(state : ChapterState):
    new_question = interrupt({"stage" : "question", "msg" : "질문이 있으신가요?"})
    return {"question" : new_question}

def moreQuestion(state : ChapterState):
    reply = interrupt(({"stage" : "more", "msg" : "더 궁금한게 있나요? (Y/N)"}))
    return {'cont' : reply}

def done(state : ChapterState):
    return {'answer' : "문서에 대한 설명을 끝마쳤습니다"}

def clarify(state : ChapterState):
    response = clarify_chain.invoke({"text" : state['cont']})
    reply = interrupt({"stage": "clarify", "answer" : response, "msg" : ""})
    return {"cont" : reply}

def advance(state: ChapterState) -> str:
    #청크 잔여 여부
    if state['cursor'] + 1 < len(state['text']):
        return 'next_chunk'
    #if 청크 소진, 챕터 잔여 여부
    p = state['parent_index']
    c = state['chapter_index']

    if p >= max(baseline.chapter_count) and c >= baseline.chapter_count[p]:
        return 'done'

    return 'nextChapter'

def routeNode(state):
    res = classify_unclear(state['cont'])
    return {'question': state['cont'], 'check_state' : res}

def routeEdge(state) -> str:
    tmp = state['check_state']
    if tmp == 'chapter':
        return 'returnChapter'
    elif tmp == 'question':
        return 'qa'
    else:
        return 'clarify'

def clearAnswer(state : ChapterState):
    return {'answer' : ""}

#질의응답 여부
def after_ask(state : ChapterState) -> str:
    res = to_yn(state['cont'])

    if  res == 'N':
        return 'qa'
    elif res == 'unclear':
        return 'routeNode'

    return advance(state)

#추가질문 여부
def after_more(state : ChapterState) -> str:
    res = to_yn(state['cont'])

    if res == 'Y':
        return 'again'
    elif res == 'unclear':
        return 'routeNode'

    return advance(state)

# -- 그래프 엣지 --
qa_graph = qa_builder.compile() # 서브그래프용으로 체크포인터가 없는 그래프 빌드 (부모 그래프가 체크포인터가 있어 터진다!!)

builder_chapter = StateGraph(ChapterState)
builder_chapter.add_node('routeNode', routeNode)
builder_chapter.add_node('returnChapter', returnChapter)
builder_chapter.add_node('textChapter', textChapter)
builder_chapter.add_node('printChapter', printChapter)
builder_chapter.add_node('ask', ask)
builder_chapter.add_node('nextChunk', nextChunk)
builder_chapter.add_node('nextChapter', nextChapter)
builder_chapter.add_node('toQA', toQA)
builder_chapter.add_node('moreQuestion', moreQuestion)
builder_chapter.add_node('done', done)
builder_chapter.add_node('qa', qa_graph) #서브그래프노드
builder_chapter.add_node('clearAnswer', clearAnswer)
builder_chapter.add_node('clarify', clarify)

builder_chapter.add_edge(START, 'routeNode')
builder_chapter.add_conditional_edges(
    "routeNode",
    routeEdge,
    {
        'qa' : 'qa',
        'returnChapter' : 'returnChapter',
        'clarify' : 'clarify'
    })
builder_chapter.add_edge('returnChapter', 'textChapter')
builder_chapter.add_edge('textChapter', 'printChapter')
builder_chapter.add_edge('printChapter', 'ask')
builder_chapter.add_conditional_edges(
    "ask",
    after_ask,
    {
        'qa' : 'clearAnswer',
        'next_chunk' : 'nextChunk',
        'nextChapter' : 'nextChapter',
        'done' : 'done',
        'returnChapter' : 'returnChapter',
        'clarify' : 'clarify',
        'routeNode' : 'routeNode'
    }
)
builder_chapter.add_edge('clearAnswer', 'toQA')
builder_chapter.add_edge('nextChunk', 'printChapter')
builder_chapter.add_edge('nextChapter', 'textChapter')
builder_chapter.add_edge('done', END)
builder_chapter.add_edge('toQA', 'qa') #서브그래프 적용
builder_chapter.add_edge('qa', 'moreQuestion')
builder_chapter.add_edge('clarify', 'routeNode')
builder_chapter.add_conditional_edges(
    'moreQuestion',
    after_more,
    {
        'again' : 'clearAnswer',
        'next_chunk' : 'nextChunk',
        'nextChapter' : 'nextChapter',
        'done' : 'done',
        'returnChapter' : 'returnChapter',
        'clarify': 'clarify',
        'routeNode' : 'routeNode'
    }
)

graph_chapter = builder_chapter.compile(checkpointer=MemorySaver())
