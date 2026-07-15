#import
import os
from collections import defaultdict

import pymupdf
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from personal_project.prompt import toc_prompt

load_dotenv()
from pydantic import BaseModel, Field

#환경변수
EMBEDDED = os.environ.get("EMBEDED")
FILEPATH = os.environ.get("FILEPATH")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP"))
DB = os.environ.get("DB")
TOP_K = int(os.environ.get("TOP_K"))

os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.environ.get("lang_smith")
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "personal_project"
os.environ["GOOGLE_API_KEY"] = os.environ.get("google_api_key")

#llm 모델
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 0)

#계층화된 목차를 위해 스키마 정의하기
class Chapter(BaseModel):
    level : int = Field(description="계층. 1이면 대챕터, 2면 세부 챕터")
    title : str
    page : int = Field(description="챕터가 시작하는 페이지 번호")

class Outline(BaseModel):
    chapters : list[Chapter]

#문서 로딩
doc = pymupdf.open(FILEPATH)
toc = doc.get_toc()
count = 0

if toc:
    toc_structure = llm.with_structured_output(Outline)
    toc_chain = toc_prompt | toc_structure
    result = toc_chain.invoke({"toc_list" : toc})
    print(result)
else: #글자수를 세기 위해 block -> line -> span 단위로 들어가서 텍스트 정보 확인
    word_count = defaultdict(int)
    for page in doc:
        d = page.get_text("dict")
        for block in d['blocks']:
            if 'lines' in block:  # 이미지의 경우 라인이 없다
                for line in block['lines']:
                    for span in line['spans']:
                        count += 1
                        size = round(span['size'], 0)
                        text = span['text']
                        font = span['font']
                        flags = span['flags']

                        #딕셔너리에는 immutable이 들어가야 하는데 list의 경우에는 가변의 성격을 띄고 있으므로 넣어주면 에러가 발생함
                        word_count[(size, flags)] += len(text) #덮어쓰기 말고 누적이 되도록

    print(word_count)
    body_info = max(word_count, key=word_count.get)

    res = []
    #본문 제외한 내용만 추출하기
    for page_num, page in enumerate(doc, start=1):
        d = page.get_text("dict")
        for block in d['blocks']:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        size = round(span['size'], 0)
                        text = span['text'].strip()
                        font = span['font']
                        flags = span['flags']

                        if body_info[0] != size and text:
                            res.append([text, page_num])

    print(res)
    noToc_structure = llm.with_structured_output(Outline)
    noToc_chain = toc_prompt | noToc_structure
    respond = noToc_chain.invoke({"toc_list" : res})
    print(respond)