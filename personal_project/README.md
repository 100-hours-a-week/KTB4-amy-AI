# Docent AI

pdf 문서를 업로드 하면 챕터 단위로 순차 설명 및 질의응답 기능을 지원하는 LangGraph 기반 RAG 튜터링 시스템

## Features
- **Feature 1** — PDF 문서 업로드 : 업로드한 문서를 전처리합니다. 
- **Feature 2** — 문서 챕터화 및 분할 설명 : LLM이 목차 구조(대챕터/세부챕터)를 뽑아 챕터별로 설명합니다. 
- **Feature 3** — 검색(rag, 웹) : 문서에서 답을 찾되 유사도 기반 검색으로 일정 수준 이하면 웹 검색으로 전환합니다.

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Gemini API 키, Anthropic(Claude) API 키

### 환경 변수
```
google_api_key=...
google_api_key2=...        # 폴백용 (선택)
claude_api_key=...
MODEL=gemini-3.5-flash-lite
MODEL_C=claude-sonnet-...
EMBEDED=intfloat/multilingual-e5-base
DB=/절대경로/chroma_db
CHUNK_SIZE=...
CHUNK_OVERLAP=...
TOP_K=...
```

### Installation
 
```bash
# 백엔드
pip install -r requirements.txt
 
# 프론트엔드
cd frontend
npm install
```

### Run
 
```bash
# 백엔드 (리포 루트에서)
uvicorn personal_project.main:app --reload
 
# 프론트엔드
cd frontend
npm run dev
```

## Usage

 1. pdf 문서 업로드
 2. "1챕터 설명해줘" 또는 "~~ 개념부터" 와 같은 희망하는 부분부터 학습 시작
 3. 설명을 듣던 도중 질의응답으로 전환 가능

![img](./frontend/img/Docent%20ai%201.png)
![img](./frontend/img/DocentAI2.png)
![img](./frontend/img/DocentAI3.png)

## Architecture
 
```
[React 프론트]
      │  /upload · /ask · /resume
      ▼
[FastAPI]
      │
      ▼
[LangGraph — 순차 교육 그래프]
   routeNode(의도 분류)
      ├─ chapter ─→ returnChapter → textChapter → printChapter → ask
      ├─ question ─→ QA 서브그래프
      └─ clarify ─→ 응대 생성 → 재분류
 
   [QA 서브그래프 — Corrective RAG]
   initialize → search → evaluate → (충분? learn / 부족? ask·retry·web_search)
```
 
### 기술 스택
 
| 구분 | 사용 기술 |
|------|-----------|
| 오케스트레이션 | LangGraph (StateGraph, interrupt, MemorySaver) |
| LLM | Gemini 3.5 Flash lite (분류·QA), Claude Sonnet (챕터 설명) |
| 임베딩 | multilingual-e5-base (HuggingFace) |
| 벡터 스토어 | Chroma |
| 웹 검색 | ddgs (DuckDuckGo) |
| 백엔드 / 프론트 | FastAPI / React |

## API Reference

### `Client(options)`
REST API로 제공되며, 세 엔드포인트 모두 `POST`입니다. 대화는 `/ask`로 시작해 `thread_id`를 발급받고, 응답이 `interrupted`이면 사용자 입력을 받아 같은 `thread_id`로 `/resume`를 반복합니다. (LLM API 키는 서버의 `.env`로 설정하며, 클라이언트가 전달하지 않습니다.)
 
### `POST /upload`
 
PDF를 업로드하고 색인(벡터 스토어)을 생성합니다. `multipart/form-data`로 전송합니다.
 
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | ✓ | 업로드할 PDF |
 
**Returns**
 
```json
{ "filename": "lecture.pdf" }
```
 
### `POST /ask`
 
첫 입력을 보내 대화를 시작합니다.
 
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | ✓ | 사용자 입력 (챕터 요청 또는 질문) |
| `thread_id` | string \| null | | 이어가기용 식별자. 첫 요청은 `null`이면 새로 발급 |
 
**Returns:** 공통 응답 객체 (아래 참고)
 
### `POST /resume`
 
중단된 지점을 이어갑니다. `/ask`에서 받은 `thread_id`를 그대로 사용해야 대화 맥락이 유지됩니다.
 
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thread_id` | string | ✓ | `/ask`에서 발급받은 대화 식별자 |
| `reply` | string | ✓ | 직전 `stage`에 대한 사용자 응답 (Y/N 또는 자유 입력) |
 
**Returns:** 공통 응답 객체 (아래 참고)
### 공통 응답 객체
 
```json
{
  "status": "interrupted",
  "thread_id": "생성된-uuid",
  "stage": "yn",
  "msg": "이어서 다음 내용을 설명할까요? (Y/N)",
  "answer": "챕터 설명 내용..."
}
```
 
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `interrupted` (사용자 입력 대기) 또는 `completed` (대화 종료) |
| `thread_id` | string | 대화 식별자. 이후 모든 `/resume`에 그대로 실어야 함 |
| `stage` | string | 지금 기다리는 입력의 종류 (아래 표) |
| `msg` | string | 사용자에게 보여줄 안내/질문 문구 |
| `answer` | string \| null | 생성된 설명 또는 답변 |
 
**`stage` 값**
 
| Value | Description | 기대 입력 |
|-------|-------------|-----------|
| `yn` | 이어서 설명할지 | Y / N |
| `more` | 추가 질문이 있는지 | Y / N |
| `question` | 질문 자유 입력 | 질문 문장 |
| `clarify` | 입력이 애매해 되물음 | 자유 입력 |
| `websearch` | 웹 검색으로 전환할지 | Y / N |

## License

 MIT License. 

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) — 랭그래프
- [Chroma](https://www.trychroma.com/) — 벡터 스토어
- [multilingual-e5](https://huggingface.co/intfloat/multilingual-e5-base) — 임베딩 모델