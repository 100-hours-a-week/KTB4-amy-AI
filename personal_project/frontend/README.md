# 학습 보조 AI — 프론트엔드

FastAPI 백엔드(`/upload`, `/ask`, `/resume`)에 붙는 React(Vite) 프론트엔드입니다.
지금은 "업로드 → 채팅 1회" 흐름만 지원하고, 노트 저장/선택(NotebookLM 방식)은 추후 확장 예정입니다.

## 요구사항

- Node.js 20+ / npm
- Python 3.13+ / [uv](https://docs.astral.sh/uv/)
- 백엔드 루트(`..`)에 `claude_api_key`, `google_api_key` 등 필요한 키가 담긴 `.env` 파일

## 설치 및 실행

**1. 백엔드**

```bash
cd ..                # 저장소 루트 (personal_project)
uv sync               # pyproject.toml 기준 의존성 설치 (.venv 생성)
.venv/bin/uvicorn main:app --port 8000
```

**2. 프론트엔드** (별도 터미널)

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173`에서 열립니다. 백엔드(`http://localhost:8000`)가 먼저 떠 있어야 정상 동작합니다.

## 환경변수

프론트엔드 `.env`에서 백엔드 주소를 설정합니다.

```
VITE_API_BASE_URL=http://localhost:8000
```

백엔드에 CORS(`CORSMiddleware`)가 `http://localhost:5173`을 허용하도록 설정되어 있어야 합니다.

## 백엔드 API 계약

- `POST /upload` (multipart, `file`) → `{ filename }`
- `POST /ask` (`{ question, thread_id? }`) → `{ status, thread_id, stage?, msg?, answer? }`
- `POST /resume` (`{ thread_id, reply }`) → 위와 동일한 응답 형태

`status`가 `"interrupted"`이면 `stage`에 따라 입력 UI가 달라집니다:

| stage | 의미 | 입력 UI |
|---|---|---|
| `yn` / `more` | Y/N 질문 | 텍스트 입력(자유 응답도 허용) |
| `question` | 새 질문 받기 | 텍스트 입력 |
| `clarify` | 애매한 입력에 대한 재질문 | 텍스트 입력 |

`status`가 `"completed"`이면 그래프가 끝난 것이므로 더 이상 입력을 받지 않습니다.
첫 `/ask` 응답의 `thread_id`를 저장해 이후 모든 `/resume` 요청에 실어 보냅니다.

## 프로젝트 구조

```
src/
  api/client.js              # /upload, /ask, /resume 호출 래퍼
  stages.js                  # stage별 placeholder, Y/N stage 목록
  components/
    NotebookWorkspace.jsx    # upload ↔ chat 단계 전환을 소유 (추후 노트 목록이 이 컴포넌트를 여러 개 렌더하게 될 자리)
    UploadPanel.jsx          # PDF 업로드, 분석 중 로딩 표시
    ChatPanel.jsx            # thread_id 유지, ask/resume 루프, 자동 스크롤
    StageInput.jsx           # stage에 맞춘 입력 UI
    ChatMessage.jsx          # 메시지 말풍선 + 마크다운 렌더링
    TypingIndicator.jsx      # 응답 대기 중 점 애니메이션
```

## 알려진 제약

- 노트 저장/여러 문서 관리 기능 없음 (`NotebookWorkspace` 하나만 렌더링, 새로고침 시 대화 초기화)
- 백엔드가 재시작되면 서버 쪽 `thread_id` 상태(MemorySaver)도 사라짐
