# classifiers.py
from personal_project.baseline import llm
from pydantic import BaseModel
from typing import Literal

class ynModel(BaseModel):
    answer: Literal["Y", "N", "unclear"]

class unclearModel(BaseModel):
    answer: Literal["chapter", "question", "clarify"]

def to_yn(text):
    t = text.strip().upper()

    if t in ('Y', 'YES', '응', '네', 'ㅇㅇ'):
        return 'Y'
    elif t in ('N', 'NO', "아니", "아니요", 'ㄴㄴ'):
        return 'N'

    yn_llm = llm.with_structured_output(ynModel)
    result = yn_llm.invoke(text)

    return result.answer

def classify_unclear(text):
    classify_llm = llm.with_structured_output(unclearModel)
    result = classify_llm.invoke(text)
    return result.answer