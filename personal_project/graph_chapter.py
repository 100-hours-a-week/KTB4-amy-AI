from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel
from typing_extensions import TypedDict

from personal_project.baseline import retriever, format_docs, llm, chunks
from personal_project.prompt import prompt

class Index(BaseModel):
    parent_index : int
    chapter_index : int

class ChapterState(TypedDict):
    question: str
    parent_index : int
    chapter_index : int
    text : list

def returnChapter(state : ChapterState):
    chapter_structure = llm.with_structured_output(Index)
    chapter_chain = ( {'context' : retriever | format_docs, 'question' : RunnablePassthrough()}
            | prompt | chapter_structure)
    return {'parent_index' : chapter_chain.parent_index, 'chapter_index' : chapter_chain.chapter_index}

def textChapter(state : ChapterState):
    pr = state['parent_index']
    ch = state['chapter_index']

    tmp = []
    num = 0
    for i in chunks:
        if i.metadata['parent_index'] == pr and i.metadata['chapter_index'] == ch:
            i.metadata['chunk_index'] = num
            tmp.append([i])
            num += 1

    return {'text' : tmp}

def printChapter(state : ChapterState):
    string = state['text']


