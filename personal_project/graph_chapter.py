from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel
from typing_extensions import TypedDict

from personal_project.baseline import retriever, llm, vectorstore, chapter_count
from personal_project.graph import builder as qa_builder
from personal_project.prompt import chapter_prompt, lecture_prompt


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

def format_with_index(docs):
    return "\n\n".join(
        f"[parent_index={d.metadata['parent_index']}, chapter_index = {d.metadata['chapter_index']}]{d.page_content}"
        for d in docs
    )

def returnChapter(state : ChapterState):
    chapter_structure = llm.with_structured_output(Index)
    chapter_chain = ( {'context' : retriever | format_with_index, 'question' : RunnablePassthrough()}
            | chapter_prompt | chapter_structure)
    result = chapter_chain.invoke(state['question'])
    return {'parent_index' : result.parent_index, 'chapter_index' : result.chapter_index}

def textChapter(state : ChapterState):
    pr = state['parent_index']
    ch = state['chapter_index']
    print(f"=== textChapter 조회: parent_index={pr}, chapter_index={ch}")

    tmp = vectorstore.get(where={"$and" : [ #연산자 시퀄문용 $ == chroma 연산자
        {"parent_index" : pr},
        {"chapter_index" : ch},
    ]})
    print(f"=== 조회 결과 청크 수: {len(tmp['documents'])}")

    items = list(zip(tmp['documents'], tmp['metadatas'])) #rawdata를 page_content, metadata 형식으로 묶어주기
    items.sort(key = lambda x : x[1]['chunk_index'])
    docs = [Document(page_content = c, metadata = m) for c,m in items]
    return {'text' : docs, 'cursor' : 0} #청크 인덱싱 초기화용

def printChapter(state : ChapterState):
    string = state['text'][state['cursor']]
    lecture_chain = (lecture_prompt | llm | StrOutputParser())
    answer = lecture_chain.invoke({'context' : string.page_content})
    return {'answer' : answer}

def ask(state : ChapterState):
    reply = interrupt({"stage" : "yn", "msg" : "이어서 다음 내용을 설명할까요? (Y/N)"})
    return {'cont' : reply}

def nextChunk(state : ChapterState):
    return {'cursor' : state['cursor'] + 1}

def nextChapter(state : ChapterState):
    p = state['parent_index']
    c = state['chapter_index']

    if c < chapter_count[p]:
        return {'chapter_index' : c + 1}
    else:
        return {'parent_index' : p + 1, 'chapter_index' : 1}

def toQA(state : ChapterState):
    new_question = interrupt({"stage" : "question", "msg" : "무엇이 궁금하신가요?"})
    return {"question" : new_question}

def moreQuestion(state : ChapterState):
    reply = interrupt(({"stage" : "more", "msg" : "더 궁금한게 있나요? (Y/N)"}))
    return {'cont' : reply}

def done(state : ChapterState):
    return {'answer' : "문서에 대한 설명을 끝마쳤습니다"}

def advance(state: ChapterState) -> str:
    #청크 잔여 여부
    if state['cursor'] + 1 < len(state['text']):
        return 'next_chunk'
    #if 청크 소진, 챕터 잔여 여부
    p = state['parent_index']
    c = state['chapter_index']

    if p >= max(chapter_count) and c >= chapter_count[p]:
        return 'done'

    return 'nextChapter'

#질의응답 여부
def after_ask(state : ChapterState) -> str:
    if  state['cont'].strip().upper().startswith('N'):
        return 'qa'
    elif state['cont'].strip().startswith('아니'):
        return 'qa'
    return advance(state)

#추가질문 여부
def after_more(state : ChapterState) -> str:
    if state['cont'].strip().upper().startswith('N'):
        return advance(state)
    elif state['cont'].strip().startswith('아니'):
        return advance(state)
    return 'again'


# -- 그래프 엣지 --
qa_graph = qa_builder.compile() # 서브그래프용으로 체크포인터가 없는 그래프 빌드 (부모 그래프가 체크포인터가 있어 터진다!!)

builder_chapter = StateGraph(ChapterState)
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

builder_chapter.add_edge(START, 'returnChapter')
builder_chapter.add_edge('returnChapter', 'textChapter')
builder_chapter.add_edge('textChapter', 'printChapter')
builder_chapter.add_edge('printChapter', 'ask')
builder_chapter.add_conditional_edges(
    "ask",
    after_ask,
    {
        'qa' : 'toQA',
        'next_chunk' : 'nextChunk',
        'nextChapter' : 'nextChapter',
        'done' : 'done'
    }
)
builder_chapter.add_edge('nextChunk', 'printChapter')
builder_chapter.add_edge('nextChapter', 'textChapter')
builder_chapter.add_edge('done', END)
builder_chapter.add_edge('toQA', 'qa') #서브그래프 적용
builder_chapter.add_edge('qa', 'moreQuestion')
builder_chapter.add_conditional_edges(
    'moreQuestion',
    after_more,
    {
        'again' : 'toQA',
        'next_chunk' : 'nextChunk',
        'nextChapter' : 'nextChapter',
        'done' : 'done'
    }
)

graph_chapter = builder_chapter.compile(checkpointer=MemorySaver())
