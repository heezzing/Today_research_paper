# Today_research_paper

매일 오전 9시 (KST) AI 분야 논문을 자동 수집하고, GitHub Models로 리뷰를 생성하여 수신자별 맞춤 이메일로 발송하는 자동화 시스템입니다.

## 파이프라인

```
[HuggingFace 트렌딩 논문 수집] → [Jina Reader 전문 fetch] → [GitHub Models 리뷰 생성] → [Gmail 발송]
```

- 실행 주기: 매일 00:00 UTC (09:00 KST), GitHub Actions
- 논문 출처: Hugging Face Daily Papers (커뮤니티 upvote 기반 트렌딩)
- 리뷰 모델: `gpt-4o-mini` (GitHub Models, GITHUB_TOKEN으로 무료 사용)

## 수신자 설정

| 수신자 | 논문 수 | 수집 방식 |
|---|---|---|
| 수신자 1 | 2편 | AI 트렌딩 상위 2편 |
| 수신자 2 | 3편 | Physical AI / VLA 키워드 필터링 (없으면 트렌딩 대체) |

> 수신자 이메일은 환경변수(`RECIPIENT_EMAIL`, `RECIPIENT_2_EMAIL`)로 관리

## 프로젝트 구조

```
mcp-servers/
├── daily_review.py             # 메인 스크립트 (수집 → 리뷰 → 발송)
├── requirements.txt            # openai, requests
├── .env                        # 수신자 이메일 등 환경변수 (git 제외)
├── .github/
│   └── workflows/
│       └── daily_review.yml   # GitHub Actions 스케줄 워크플로우
└── AI_research_paper/          # ScholarScope MCP 서버 (로컬 개발용)
    ├── src/
    │   ├── server.py
    │   ├── api_requests.py
    │   ├── schemas.py
    │   └── utils.py
    └── pyproject.toml
```

## GitHub Actions Secrets 설정

| Secret | 설명 |
|---|---|
| `GITHUB_TOKEN` | 자동 제공 — 별도 등록 불필요 |
| `GMAIL_USER` | 발신 Gmail 주소 |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 |
| `RECIPIENT_EMAIL` | 수신자 1 이메일 |
| `RECIPIENT_2_EMAIL` | 수신자 2 이메일 |

## 로컬 실행

```bash
# .env 파일에 환경변수 설정
cp .env.example .env  # 또는 직접 작성

export GITHUB_TOKEN=your_github_token
pip install -r requirements.txt
python daily_review.py
```

## MCP 서버 (로컬 개발)

Claude Code에서 논문 리뷰를 직접 요청할 때 사용하는 MCP 서버들:

| MCP 서버 | 역할 |
|---|---|
| `scholarscope` | OpenAlex API로 논문 검색 및 전문 fetch |
| `arxiv` | arxiv 전용 검색 및 트렌드 분석 |
| `filesystem` | 로컬 파일 접근 |
| `google-drive` | 결과물 저장/공유 |

ScholarScope MCP 실행:
```bash
cd AI_research_paper
uv run fastmcp run src/server.py
```
