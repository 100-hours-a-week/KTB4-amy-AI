from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.types import interrupt
from pydantic import BaseModel
from typing_extensions import TypedDict

from personal_project.baseline import retriever, format_docs, llm, chunks, vectorstore, chapter_count
from personal_project.prompt import prompt, chapter_prompt, lecture_prompt


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

    tmp = vectorstore.get(where={"$and" : [ #연산자 시퀄문용 $ == chroma 연산자
        {"parent_index" : pr},
        {"chapter_index" : ch},
    ]})
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



