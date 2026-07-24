#문서로딩, 인덱싱 등 그래프 데이터 전처리 및 프롬프트 입력
import os
import re
import unicodedata

from pydantic import BaseModel, Field
from personal_project.prompt import prompt, toc_prompt
from dotenv import load_dotenv

load_dotenv()

#환경변수 받아오기
EMBEDDED = os.environ.get("EMBEDED")
FILEPATH = os.environ.get("FILEPATH")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP"))
DB = os.environ.get("DB")
db2 = os.environ.get("db2")
TOP_K = int(os.environ.get("TOP_K"))

os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.environ.get("lang_smith")
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "personal_project"
os.environ["GOOGLE_API_KEY"] = os.environ.get("google_api_key")

#import
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

#서브 챕터 생성 - 형식 지정 (rag 이용하면 너무 대용량 넣는거 해결될듯)
class Chapter(BaseModel):
    level : int = Field(description="계층. 1이면 대챕터, 2부터는 세부 챕터")
    title : str
    start_index : int = Field(description="챕터가 시작하는 리스트의 인덱스, 대챕터의 경우 대챕터에 속한 첫번째 세부 챕터의 start_index와 동일하게 할당한다")
    parent : str = Field(description="대챕터면 parent는 비워두고 세부 챕터면 소속 대챕터 제목 삽입")
    last_index : int = Field(description="챕터가 시작하는 마지막 인덱스, 대챕터의 경우 대챕터에 속한 마지막 세부 챕터의 last_index와 동일하게 할당한다")

class Outline(BaseModel):
    chapters : list[Chapter]

#임베딩 - 구글 api 소모 속도가 생각보다 빨라서 임시로 허깅 페이스 사용 중
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDED,
    encode_kwargs={"prompt": "passage: ", "normalize_embeddings": True},
    query_encode_kwargs={"prompt": "query: ", "normalize_embeddings": True},
)

#문서 로드
all_docs = []
if os.path.exists(FILEPATH):
    loader = PyMuPDFLoader(FILEPATH)
    all_docs.extend(loader.load())

#전처리 함수
def preprocess_text(text):
    text = unicodedata.normalize("NFKC", text) # 아니 특수문자 정규화해서 제거하려고 했는데 이걸로 \uf07d가 안없어짐!!!
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\xad]", "", text) #특수문자 제거용
    text = re.sub(r"[ \t]+", " ", text) # 공백 통일용
    text = re.sub(r"\n{3,}", "\n\n", text) #줄넘김 통일용
    text = re.sub(r"[\uE000-\uF8FF]", "", text) #그래서 이걸로 없애줬어요
    return text.strip()

#문서 로드 및 전처리
cleaned_docs = []
for i in all_docs:
    text = i.page_content

    if text:
        text = preprocess_text(text)
        cleaned_docs.append(text)

#서브챕터 - 랭체인
toc_llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature = 0, max_retries = 0, api_key = os.environ.get("google_api_key2"))
toc_structure = toc_llm.with_structured_output(Outline)
toc_chain = toc_prompt | toc_structure

#개발 중 임시 저장 용
toc_cache = "toc_cache.json"
res = None

if os.path.exists(toc_cache):
    try:
        with open(toc_cache, encoding="utf-8") as f:
            res = Outline.model_validate_json(f.read())
    except:
        res = None
if res == None:
    numbered = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(cleaned_docs))
    res = toc_chain.invoke({"toc_list": numbered})
    with open(toc_cache, "w", encoding="utf-8") as f:
        f.write(res.model_dump_json(indent=2)) #indent : 들여쓰기

chapter_num = 1
parent_num = 0

docs = []
tmp = 0

for ch in res.chapters:
    level = ch.level
    title = ch.title
    start_index = ch.start_index
    last_index = ch.last_index
    parent = ch.parent

    if level == 1:
        chapter_num = 1
        parent_num += 1
    else:
        for i in range(start_index, last_index + 1, 1):
            doc = Document(page_content=cleaned_docs[i], metadata = {'title' : title, 'level' : level,  'parent' : parent, 'chapter_index' : chapter_num, 'parent_index' : parent_num})
            docs.append(doc)
        chapter_num += 1

#청킹
splitter = RecursiveCharacterTextSplitter(
    chunk_size = CHUNK_SIZE,
    chunk_overlap = CHUNK_OVERLAP,
)
chunks = splitter.split_documents(docs)

#청킹 인덱싱 해주기
n = 1
for c in chunks:
    if c.metadata['chapter_index'] == 1 and n == 1:


print(f"청킹 데이터 : {chunks[0]}...")

#db
#NOTE : db가 없을때만 생성되도록

if (os.path.exists(DB)) != True:
  vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB,
  )
  print("인덱싱 완료. Chroma 저장 위치:", DB)
else: #벡터디비가 이미 존재하면 호출을 해주도록 하자
  vectorstore = Chroma(
      persist_directory = DB,
      embedding_function = embeddings
  )

#RAG 체인
#HACK : 왜인지는 모르겠는데 llm이 성공적으로 호출되어도 계속 호출하는 현상이 있어서 최대 호출횟수 지정해서 해결 하였음
#NOTE : 아니 근데 출력 결과 너무 맘에 안드는데 맘에 드는 결과 나올때까지 작성하자니 프롬프트 너무 길어질것 같고
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 0)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# #테스트
# test_q = "니체가 말하는 삶이 뭐야?"
# print("Q:", test_q)
# print("A:", rag_chain.invoke(test_q))
#
# test_q = "이해가 안됐어 디오니소스라니?"
# print("Q:", test_q)
# print("A:", rag_chain.invoke(test_q))


# 평가 되는거 확인 완료, api 사용 한도 때문에 잠시 주석 처리 (fastapi 확인해야함,,)
# def contains_expected_keyword(run, example):
#     pred = run.outputs.get("answer", "")
#     expected = example.outputs.get("answer", "")
#
#     keywords = [w for w in expected.split() if len(w) >= 2][:2]
#     hit = all(k in pred for k in keywords)
#
#     return {
#         "key": "contains_expected_keyword",
#         "score": 1 if hit else 0,
#         "comment": f"필수 키워드 {keywords} 포함 여부",
#     }
#
# #데이터셋 생성
# assert "rag_chain" in dir(), "rag_chain이 존재하지 않습니다"
# assert "llm" in dir(), "llm이 존재하지 않습니다"
#
#
# client = Client()
#
# DATASET_NAME = "personal-project-eval"
#
# existing = [d for d in client.list_datasets(dataset_name = DATASET_NAME)]
#
# if existing:
#   dataset = existing[0]
# else:
#   dataset = client.create_dataset(
#       dataset_name = DATASET_NAME,
#       description = 'rag 품질 평가용'
#   )
#
# print(dataset.id)
#
# #평가
# client.create_examples(
#     dataset_id = dataset.id,
#     inputs = [
#         {"question" : "관점주의란"},
#         {"question" : "주황색"},
#         {"question" : "니체가 말하는 삶이 뭐야?"},
#     ],
#     outputs = [
#         {"answer" : '''관점주의는 진리가 다양한 관점들의 충돌과 해석의 산물이라고 보며, 모든 관점이 동등한 가치를 갖지 않고 삶에 더 봉사하는 관점이 우월하다고 주장합니다. 이는 관점들의 끊임없는 충돌과 경쟁이라는 역동적인 과정에 주목하며, 더 높은 수준의 창조적이고 삶을 긍정하는 관점이 그렇지 않은 관점을 극복한다고 봅니다. 관점주의는 모든 해석을 의심하고 새로운 가치를 창조하려는 적극적인 태도를 요구하며, '보다 나은 관점'을 향해 나아가는 것을 목표로 합니다.
#
# 또한 관점주의에서 '나'라는 주체는 고정된 실체가 아닌 다양한 힘과 충동의 역동적 결합체이며, 새로운 관점을 창조함으로써 삶을 확장하고 강화하려는 '힘에의 의지'와 연결된 능동적인 행위입니다. 주관주의와 달리, 관점은 한 개인의 의식이나 마음의 산물이 아니라 생명체로서 '몸', 곧 특정 생명체가 처한 생리학적, 심리적 조건이 세계를 해석하는 방식을 의미합니다. 따라서 관점주의는 절대적 진리를 부정하고 다양한 관점의 존재를 긍정하며, 삶을 긍정하고 새롭게 창조하기 위한 해석을 시도하고 삶에 봉사하는 새로운 가치의 창조를 추구합니다.'''},
#         {"answer" : "자료에서 찾을 수 없습니다"},
#         {"answer" : '''제시된 문서에 따르면, 니체가 말하는 삶은 다음과 같은 특징을 가집니다.
#
# 첫째, 삶은 **스스로 경험 상황을 구성하고 창조하는 과정**입니다. 그는 자신의 삶을 위한 관점적 경험 상황을 스스로 만들고, 그 상황에 의미와 가치를 부여함으로써 모든 순간이 자신에게 의미 있고 필연적임을 아는 자입니다.
#
# 둘째, 이러한 삶은 **고통의 영원한 회귀를 확고히 의지하는 것**을 포함합니다. 이는 고통을 더 이상 정당화할 필요 없이 받아들이고 긍정하는 태도를 의미합니다.
#
# 셋째, 그는 **자신의 힘을 확신하고 인간이 도달한 힘에 긍지를 가지는 자**입니다. 이는 자기 자신과 인간의 잠재력에 대한 강한 믿음과 자부심을 나타냅니다.
#
# 요약하자면, 니체에게 삶은 **미학적(창조적) 해석을 통한 디오니소스적 자기긍정의 삶**입니다. 이는 자신의 삶을 예술 작품처럼 창조하고, 그 안에서 고통까지도 긍정하며, 자신의 힘과 가치를 확신하는 삶을 의미합니다.
#
# 제가 설명해 드린 내용이 니체가 말하는 삶의 개념을 이해하는 데 도움이 되셨을까요? 혹시 더 궁금하거나 헷갈리는 부분이 있으신가요?'''},
#     ]
# )
#
# examples = list(client.list_examples(dataset_name = DATASET_NAME))
#
# #평가 작동 확인용 - example의 question 값을 넣어 실제 답변 생성
# def target(inputs):
#   return {"answer" : rag_chain.invoke(inputs["question"])}
#
#
# #평가용 랭체인
# JUDGE_PROMPT = ChatPromptTemplate.from_messages([
#     ("system",
#      "당신은 답변 품질을 평가하는 채점자입니다.\n"
#      "아래 기대 답변(reference)과 모델 답변 (prediction)을 비교하고,\n"
#      "의미가 일치하면 1, 부분적으로만 일치하면 0.5, 무관하면 0을 점수로 매기세요.\n"
#      "점수를 출력할때에는 무조건 숫자로만 출력하도록 하세요"),
#     ("human",
#      "질문 : {question}\n\n"
#      "기대 답변: {reference}\n\n"
#      "모델 답변 : {prediction}"),
#
# ])
#
# eval_chain = JUDGE_PROMPT | llm | StrOutputParser()
#
# def llm_eval(run, example):
#   reply = eval_chain.invoke({
#       "question" : example.inputs["question"],
#       "reference" : example.outputs["answer"],
#       "prediction" : run.outputs["answer"],
#   })
#
#   first_line = reply.strip().splitlines()[0].strip()
#   try:
#     score = float(first_line)
#   except ValueError:
#     score = 0
#   return{
#       "key": "llm_judge_semantic_match",
#       "score": score,
#       "comment": reply,
#   }
#
# result = evaluate(
#     target, #인보크 돌리기용
#     data = DATASET_NAME, #데이터셋
#     evaluators = [contains_expected_keyword, llm_eval], #평가함수
#     experiment_prefix = "v1-baseline" #평가 결과지 앞에 붙이는 이름
# )