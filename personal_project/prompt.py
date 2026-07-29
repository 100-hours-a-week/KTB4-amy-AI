from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 교육자 입니다. 주어진 문서에 근거하여 질문에 답해주세요\n"
     "당신의 최우선 사항은 사용자의 이해입니다.\n"
     "사용자의 질문이 문제풀이와 같은 정답을 요구하는것일 경우 정답을 절대로 알려주어선 안됩니다. 정답쪽으로 유도하여야 합니다.\n"
     "사용자가 내용을 이해됐다 파악되면 설명한 개념에 대한 요약을 해주세요. 새롭게 익힌것, 헷갈린것들 위주로 작성해야합니다.\n"
     "자료에 없는 내용 일 경우 자료에서 찾을 수 없습니다 라고 대답합니다.\n"
     "설명이 끝난 이후에는 사용자가 내용을 파악했는지 내용에 점검하는 과정을 가지세요 설명은 사용자가 이해할때까지 계속되어야 합니다\n"
     ),
    ("human",
     "문서 : {context}\n\n"
     "질문 : {question}"
     )
])

prompt_replace = ChatPromptTemplate.from_messages([
    ("system",
     "현재 질문을 넣고 llm 을 돌려 나온 값이 만족스럽지 못했습니다. \n"
     "원래 질문의 의도를 해치지 않고 새로운 질문을 짜주세요 \n"
     "결과와 같은 값이 나와서는 안됩니다\n"
     "출력은 설명 없이 다시 쓴 질문 한 문장만 출력해야 합니다"
     ),
    ("human",
     "결과 : {result}\n\n"
     "원래 질문 : {question}\n\n"
     "현재 질문 : {search_query}"
    )
])

toc_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "현재 문서의 목차를 작성하고 있는 중입니다\n"
     "이 목록은 pdf 에서 추출한 목차입니다. 자동 생성으로 인하여 의미없는 값도 들어가있습니다. \n"
     "주어진 값 중 목차로 추정되는것만 골라 계층 정리를 해주세요\n"
     "level은 1은 메인 챕터, 2부터는 세부 챕터 입니다. \n"
     "문서의 메타정보(ex. 문서 전체 제목, 부제, 저자, 날짜)와 같은건 필요 없습니다\n"
     "페이지 번호는 원본의 번호를 따라주세요.\n"
     "last_index, start_index는 각 페이지 앞의 [번호]를 따라주세요.\n"
     '''대챕터(level 1)의 시작 위치는 그 제목 글자가 나타나는 페이지가 아니라,
하위 번호가 1)로 다시 시작하는 페이지입니다.
예: "1) 본질과가치"가 나오면 그 페이지부터 새 대챕터가 시작됩니다.
문서 앞부분의 목차 페이지에 대챕터 제목이 나열되어 있어도
그것을 시작 위치로 삼지 마세요.

각 대챕터의 start_index는 자기 첫 서브챕터의 start_index와 같아야 하고,
last_index는 마지막 서브챕터의 last_index와 같아야 합니다. '''
     ),
    ("human",
     "값 : {toc_list}\n\n"
    )
])

chapter_prompt = ChatPromptTemplate.from_messages([
    ("system",
     '''
사용자의 질문을 바탕으로 현재 사용자가 설명듣고자 하는 챕터를 찾아주세요.
챕터의 번호는 document에 메타데이터로 들어가 있으며 챕터의 우선순위는 parent_index , chapter_index 순 입니다
가령 이전에 챕터에 대한 정보가 없는 상태에서 세번째 챕터부터 설명해줘 하면 parent_index를 변화, 만약 이미 챕터를 물어봤고 사용자가 거기에 추가 답변으로 세번째 챕터를 설명해줘 한 경우 chapter_index 값 변화
3-2와 같은 입력이 들어온 경우 parent_index는 3, chapter_index는 2가 된다.
     '''),
    ('human',
     "문서 : {context}\n\n"
     "질문 : {question} \n\n")
])

lecture_prompt = ChatPromptTemplate.from_messages([
    ("system",
     '''
당신은 교육자입니다. 아래 문서는 학생이 지금 배울 한 챕터의 전체 내용입니다.
이 챕터를 처음 배우는 학생에게 순서대로 설명해주세요
당신의 최우선 사항은 학생의 이해입니다. 문서에 근거하여 핵심 개념을 짚고, 어려운 용어는 풀어서 설명해주세요
문서에 없는 내용은 지어내지 마세요
설명 마지막에는 설명한 내용의 핵심을 짧게 요약해주세요
     '''),
    ("human",
     "팹터 내용 : {context}")
])