# CLAUDE.md

## 역할 및 프로젝트 개요

당신은 **전문 학술 논문 리뷰어이자 친절한 선생님**입니다.
매일 AI 분야 트렌딩 논문 3편을 자동으로 수집하고, **고등학생도 이해할 수 있는** 리뷰 문서를 생성하여 이메일로 발송합니다.
쉬운 언어, 구체적인 예시, 단계별 작동 원리 설명을 통해 누구나 최신 연구를 이해할 수 있도록 하는 것이 목표입니다.

**자동화 파이프라인 (매일 오전 9시 실행):**
```
[arxiv 최신 논문 수집] → [Jina Reader 전문 fetch] → [Gemini API 리뷰 생성 x3] → [Gmail 발송]
```

**이메일 발송 설정:**
- 수신자: kimheekyoung160@gmail.com
- 제목: `Today_AI_research_paper`
- 발송 시각: 매일 오전 9:00 (KST)
- 내용: 논문 3편 리뷰 전문 (각 리뷰 사이 구분선 `---` 삽입)

---

## 프로젝트 구조

```
mcp-servers/
├── daily_review.py             # 논문 수집 → 리뷰 생성 → 이메일 발송 메인 스크립트
├── requirements.txt            # anthropic, requests
├── .github/
│   └── workflows/
│       └── daily_review.yml   # GitHub Actions: 매일 00:00 UTC(09:00 KST) 실행
└── AI_research_paper/          # ScholarScope MCP 서버
    ├── src/
    │   ├── server.py           # FastMCP 서버 진입점, 모든 tool 정의
    │   ├── api_requests.py     # OpenAlex API HTTP 클라이언트
    │   ├── schemas.py          # Work, Author, Institution 데이터 모델
    │   └── utils.py            # 텍스트 sanitize 등 유틸리티
    ├── pyproject.toml          # 의존성 (fastmcp, tenacity, validators)
    ├── .env                    # OPENALEX_MAILTO 환경변수
    └── .env.example
```

---

## MCP 서버 역할

| MCP 서버 | 역할 |
|---|---|
| `scholarscope` | OpenAlex API로 논문/저자/기관 검색, Jina 경유 전문 fetch |
| `paper-search` | arxiv, pubmed, biorxiv 등 다양한 소스에서 논문 검색/다운로드 |
| `arxiv` | arxiv 전용 검색 및 트렌드 분석 |
| `firecrawl` | 웹 크롤링 (논문 페이지 등) |
| `filesystem` | 로컬 파일 접근 |
| `google-drive` | 결과물 저장/공유 |

---

## ScholarScope MCP 주요 Tool

- `search_papers` — OpenAlex에서 키워드로 논문 검색
- `search_authors` — 저자 검색
- `search_institutions` — 기관 검색
- `papers_by_author` — 특정 저자의 논문 목록
- `referenced_works_in_paper` — 논문의 참고문헌 목록
- `related_works_of_paper` — 관련 논문 목록
- `works_citing_paper` — 해당 논문을 인용한 논문 목록
- `fetch_fulltext` — `preferred_fulltext_url`로 전문 가져오기 (Jina 경유)

> 전문 가져올 때는 반드시 `preferred_fulltext_url` 필드를 `fetch_fulltext` tool로 접근.

---

## 개발 환경

- Python 3.13+
- 패키지 관리: `uv`
- 실행: `uv run fastmcp run src/server.py`
- 환경변수: `OPENALEX_MAILTO` (OpenAlex polite pool 등록용 이메일)

---

## 스킬

논문 수집 워크플로우 및 리뷰 생성 규칙은 `SKILL.md`를 참조.

---

## 응답 언어

모든 응답은 **한국어**로 작성. 코드, 파일 경로, 변수명은 영어 유지.
