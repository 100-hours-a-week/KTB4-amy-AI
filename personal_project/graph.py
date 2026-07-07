#랭체인 -> 랭그래프 기술 마이그레이션력

from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser  #파서용
from langchain_core.runnables import RunnablePassthrough
from langsmith import Client
from langsmith.evaluation import evaluate

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#테스트
test_q = "니체가 말하는 삶이 뭐야?"
print("Q:", test_q)
print("A:", rag_chain.invoke(test_q))

#실패 테스트
test_q = "전통적 세계해석에 대한 비판이 뭐야?"
print("Q:", test_q)
print("A:", rag_chain.invoke(test_q))

def contains_expected_keyword(run, example):
    pred = run.outputs.get("answer", "")
    expected = example.outputs.get("answer", "")

    keywords = [w for w in expected.split() if len(w) >= 2][:2]
    hit = all(k in pred for k in keywords)

    return {
        "key": "contains_expected_keyword",
        "score": 1 if hit else 0,
        "comment": f"필수 키워드 {keywords} 포함 여부",
    }

#데이터셋 생성
assert "rag_chain" in dir(), "rag_chain이 존재하지 않습니다"
assert "llm" in dir(), "llm이 존재하지 않습니다"


client = Client()

DATASET_NAME = "personal-project-eval"

existing = [d for d in client.list_datasets(dataset_name = DATASET_NAME)]

if existing:
  dataset = existing[0]
else:
  dataset = client.create_dataset(
      dataset_name = DATASET_NAME,
      description = 'rag 품질 평가용'
  )

print(dataset.id)

#example 추가
client.create_examples(
    dataset_id = dataset.id,
    inputs = [
        {"question" : "관점주의란"},
        {"question" : "주황색"},
        {"question" : "니체가 말하는 삶이 뭐야?"},
    ],
    outputs = [
        {"answer" : '''관점주의는 진리가 다양한 관점들의 충돌과 해석의 산물이라고 보며, 모든 관점이 동등한 가치를 갖지 않고 삶에 더 봉사하는 관점이 우월하다고 주장합니다. 이는 관점들의 끊임없는 충돌과 경쟁이라는 역동적인 과정에 주목하며, 더 높은 수준의 창조적이고 삶을 긍정하는 관점이 그렇지 않은 관점을 극복한다고 봅니다. 관점주의는 모든 해석을 의심하고 새로운 가치를 창조하려는 적극적인 태도를 요구하며, '보다 나은 관점'을 향해 나아가는 것을 목표로 합니다.

또한 관점주의에서 '나'라는 주체는 고정된 실체가 아닌 다양한 힘과 충동의 역동적 결합체이며, 새로운 관점을 창조함으로써 삶을 확장하고 강화하려는 '힘에의 의지'와 연결된 능동적인 행위입니다. 주관주의와 달리, 관점은 한 개인의 의식이나 마음의 산물이 아니라 생명체로서 '몸', 곧 특정 생명체가 처한 생리학적, 심리적 조건이 세계를 해석하는 방식을 의미합니다. 따라서 관점주의는 절대적 진리를 부정하고 다양한 관점의 존재를 긍정하며, 삶을 긍정하고 새롭게 창조하기 위한 해석을 시도하고 삶에 봉사하는 새로운 가치의 창조를 추구합니다.'''},
        {"answer" : "자료에서 찾을 수 없습니다"},
        {"answer" : '''제시된 문서에 따르면, 니체가 말하는 삶은 다음과 같은 특징을 가집니다.

첫째, 삶은 **스스로 경험 상황을 구성하고 창조하는 과정**입니다. 그는 자신의 삶을 위한 관점적 경험 상황을 스스로 만들고, 그 상황에 의미와 가치를 부여함으로써 모든 순간이 자신에게 의미 있고 필연적임을 아는 자입니다.

둘째, 이러한 삶은 **고통의 영원한 회귀를 확고히 의지하는 것**을 포함합니다. 이는 고통을 더 이상 정당화할 필요 없이 받아들이고 긍정하는 태도를 의미합니다.

셋째, 그는 **자신의 힘을 확신하고 인간이 도달한 힘에 긍지를 가지는 자**입니다. 이는 자기 자신과 인간의 잠재력에 대한 강한 믿음과 자부심을 나타냅니다.

요약하자면, 니체에게 삶은 **미학적(창조적) 해석을 통한 디오니소스적 자기긍정의 삶**입니다. 이는 자신의 삶을 예술 작품처럼 창조하고, 그 안에서 고통까지도 긍정하며, 자신의 힘과 가치를 확신하는 삶을 의미합니다.

제가 설명해 드린 내용이 니체가 말하는 삶의 개념을 이해하는 데 도움이 되셨을까요? 혹시 더 궁금하거나 헷갈리는 부분이 있으신가요?'''},
    ]
)

examples = list(client.list_examples(dataset_name = DATASET_NAME))

#평가 작동 확인용 - example의 question 값을 넣어 실제 답변 생성
def target(inputs):
  return {"answer" : rag_chain.invoke(inputs["question"])}

#평가용 랭체인
JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 답변 품질을 평가하는 채점자입니다.\n"
     "아래 기대 답변(reference)과 모델 답변 (prediction)을 비교하고,\n"
     "의미가 일치하면 1, 부분적으로만 일치하면 0.5, 무관하면 0을 점수로 매기세요.\n"
     "점수를 출력할때에는 무조건 숫자로만 출력하도록 하세요"),
    ("human",
     "질문 : {question}\n\n"
     "기대 답변: {reference}\n\n"
     "모델 답변 : {prediction}"),

])

eval_chain = JUDGE_PROMPT | llm | StrOutputParser()

def llm_eval(run, example):
  reply = eval_chain.invoke({
      "question" : example.inputs["question"],
      "reference" : example.outputs["answer"],
      "prediction" : run.outputs["answer"],
  })

  first_line = reply.strip().splitlines()[0].strip()
  try:
    score = float(first_line)
  except ValueError:
    score = 0
  return{
      "key": "llm_judge_semantic_match",
      "score": score,
      "comment": reply,
  }

result = evaluate(
    target, #인보크 돌리기용
    data = DATASET_NAME, #데이터셋
    evaluators = [contains_expected_keyword, llm_eval], #평가함수
    experiment_prefix = "v1-baseline" #평가 결과지 앞에 붙이는 이름
)


---

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