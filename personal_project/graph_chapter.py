from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel
from typing_extensions import TypedDict

from personal_project.baseline import retriever, format_docs, llm
from personal_project.prompt import prompt

class Index(BaseModel):
    parent_index : int
    chapter_index : int

class ChapterState(TypedDict):
    question: str
    parent_index : int
    chapter_index : int

def returnChapter(state : ChapterState):
    chapter_structure = llm.with_structured_output(Index)
    chapter_chain = ( {'context' : retriever | format_docs, 'question' : RunnablePassthrough()}
            | prompt | chapter_structure)
    return {'parent_index' : chapter_chain.parent_index, 'chapter_index' : chapter_chain.chapter_index}

