<div align="center">

# **ScholarScope MCP**

_OpenAlex 기반 학술 논문 검색 MCP 서버_

</div>

## 소개

**ScholarScope MCP Server**는 [OpenAlex API](https://openalex.org/)를 활용하는 [FastMCP](https://github.com/modelcontextprotocol/fastmcp) 기반 MCP 서버입니다.  
논문·저자·기관 검색, 인용 관계 탐색, [Jina](https://jina.ai/) 경유 전문(full-text) fetch를 지원합니다.

[![Python](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/Backend-FastMCP-orange?style=for-the-badge)](https://github.com/modelcontextprotocol/fastmcp)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

---

## 주요 기능

| Tool | 설명 |
|---|---|
| `search_papers` | 키워드로 논문 검색 |
| `search_authors` | 저자 검색 |
| `search_institutions` | 기관 검색 |
| `papers_by_author` | 특정 저자의 논문 목록 |
| `referenced_works_in_paper` | 논문의 참고문헌 목록 |
| `related_works_of_paper` | 관련 논문 목록 |
| `works_citing_paper` | 해당 논문을 인용한 논문 목록 |
| `fetch_fulltext` | `preferred_fulltext_url`로 전문 가져오기 (Jina 경유) |

> 전문을 가져올 때는 반드시 `preferred_fulltext_url` 필드를 `fetch_fulltext` tool로 접근.

---

## 설치

```bash
# 1. uv 설치 (없는 경우)
pip install uv

# 2. 의존성 설치
cd AI_research_paper
uv sync

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 OPENALEX_MAILTO=your_email@example.com 입력
```

---

## 실행

```bash
# MCP 서버 실행
uv run fastmcp run src/server.py

# MCP Inspector로 로컬 테스트
npx @modelcontextprotocol/inspector uv run \
  --directory "/path/to/AI_research_paper" \
  --with fastmcp \
  fastmcp run src/server.py
```

---

## Claude Code 연동

`.mcp.json`에 아래 설정 추가:

```json
{
  "mcpServers": {
    "scholarscope": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/AI_research_paper",
        "fastmcp",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

---

## 환경변수

| 변수 | 설명 |
|---|---|
| `OPENALEX_MAILTO` | OpenAlex polite pool 등록용 이메일 (권장) |
