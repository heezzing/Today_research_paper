"""
매일 오전 9시 (KST) AI 분야 트렌딩 논문 3편을 수집하고,
GitHub Models API로 리뷰를 생성한 뒤 이메일로 발송하는 스크립트.

필요한 환경변수:
  GITHUB_TOKEN        - GitHub Actions에서 자동 제공 (별도 설정 불필요)
  GMAIL_USER          - 발신 Gmail 주소
  GMAIL_APP_PASSWORD  - Gmail 앱 비밀번호
"""

import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from openai import OpenAI
import requests
import xml.etree.ElementTree as ET


# ── 상수 ──────────────────────────────────────────────────────────────────────

RECIPIENT_EMAIL = "kimheekyoung160@gmail.com"
EMAIL_SUBJECT = "Today_AI_research_paper"
NUM_PAPERS = 3

ARXIV_API_URL = "http://export.arxiv.org/api/query"
JINA_BASE_URL = "https://r.jina.ai"

REVIEW_PROMPT = """당신은 전문 학술 논문 리뷰어이자 친절한 선생님입니다.
아래 논문을 깊이 있게 분석하되, 고등학생도 이해할 수 있을 만큼
쉬운 언어, 구체적인 예시, 그리고 작동 원리를 단계별로 설명하여
리뷰 문서를 작성해주세요. **반드시 한국어로 작성합니다.**

---

📌 논문 정보
{paper_info}

📄 논문 전문
{fulltext}

---

📋 아래 순서대로 리뷰 문서를 작성하세요.

1. **논문 개요**
   - 연구 배경 및 문제 정의
     → 어려운 개념은 일상적인 비유나 예시로 먼저 설명 후 학술 용어 소개
     → 예: "이 연구는 마치 ___ 와 같은 문제를 해결하려 합니다"
   - 연구 목적 및 접근 방식 요약 (3~5문장)

2. **작동 구조 및 원리**

   2-1. 전체 구조 한눈에 보기 (텍스트 다이어그램)
     → [입력] → [모듈A] → [모듈B] → [출력] 형식으로 표현
     → 각 박스가 무슨 역할인지 한 줄씩 설명

   2-2. 단계별 작동 원리 (STEP 1 → STEP 2 → …)
     → 각 STEP마다: 기술적 설명 / "이 단계는 마치 ___ 하는 것과 같습니다" / 이 단계가 없으면 생기는 문제

   2-3. 핵심 인과관계 및 작동 논리
     → [원인/조건] → [중간 과정] → [결과/효과] 형식으로 정리

   2-4. 핵심 수식/알고리즘 직관적 설명 (1~3개)
     → 수식 없이 말로 먼저 설명 → 일상적 비유 → 각 변수/항 풀어서 설명

   2-5. 실제 동작 예시 (Worked Example)
     → 입력값 예시 → 각 단계 통과 → 최종 출력 결과 흐름으로 서술

3. **핵심 기여 및 Novelty**
   - 기존 연구와의 차별점 3~5가지
   - 각 기여마다 "쉽게 말하면: ___" 한 줄 요약 포함

4. **유사 개념/방법론 비교**
   - 유사 선행 연구 3~5개를 비교표(table)로 정리
   - 표 아래에 고등학생 눈높이로 풀어서 설명

5. **논문의 한계점**
   - 저자가 명시한 한계 + 리뷰어 관점 추가 한계
   - 각 한계마다 "쉽게 말하면: ___" 요약

6. **종합 평가**
   - 학술적/실용적 의의 한 단락 요약
   - 추천 독자층
   - 고등학생을 위한 한줄 총평: "한마디로, 이 논문은 ___ 분야에서 ___ 을 처음으로 가능하게 만든 연구입니다"

---

⚙️ 작성 지침
- 전문 용어는 쉬운 말로 먼저 설명 후 원어 병기 (예: 인공 신경망(Neural Network))
- 도식화는 텍스트 박스 [ ] 와 화살표 → ↓ ↑ 활용
- 인과관계는 항상 [원인] → [과정] → [결과] 형식
- 섹션당 200~400자 내외 (도식·비교표 제외)
- 톤: 친절하고 명확하게, 독자가 "아, 그렇구나!" 할 수 있도록
"""


# ── 논문 수집 ─────────────────────────────────────────────────────────────────

def fetch_trending_papers(n: int = NUM_PAPERS) -> list[dict]:
    """arxiv API에서 AI 분야 최신 논문을 가져옵니다."""
    params = {
        "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": n * 3,  # 여유분 확보 후 필터링
    }
    resp = requests.get(ARXIV_API_URL, params=params, timeout=30)
    resp.raise_for_status()

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(resp.text)
    entries = root.findall("atom:entry", ns)

    papers = []
    for entry in entries:
        arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
        published = entry.find("atom:published", ns).text[:10]
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
        link = f"https://arxiv.org/abs/{arxiv_id}"

        papers.append({
            "id": arxiv_id,
            "title": title,
            "authors": ", ".join(authors[:3]) + (" 외" if len(authors) > 3 else ""),
            "published": published,
            "summary": summary,
            "link": link,
        })

        if len(papers) == n:
            break

    return papers


# ── 전문 가져오기 ──────────────────────────────────────────────────────────────

def fetch_fulltext(arxiv_id: str) -> str:
    """Jina reader로 arxiv 논문 전문을 가져옵니다."""
    url = f"{JINA_BASE_URL}/https://arxiv.org/abs/{arxiv_id}"
    try:
        resp = requests.get(url, timeout=60, headers={"Accept": "text/plain"})
        resp.raise_for_status()
        text = resp.text
        # 너무 길면 앞부분만 사용 (Claude 컨텍스트 한계 고려)
        return text[:12000] if len(text) > 12000 else text
    except Exception as e:
        print(f"[WARN] 전문 가져오기 실패 ({arxiv_id}): {e}")
        return "(전문을 가져오지 못했습니다. 초록으로 대체합니다.)"


# ── 리뷰 생성 ─────────────────────────────────────────────────────────────────

def generate_review(paper: dict, fulltext: str) -> str:
    """GitHub Models API로 논문 리뷰를 생성합니다."""
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    paper_info = (
        f"제목: {paper['title']}\n"
        f"저자: {paper['authors']}\n"
        f"발행일: {paper['published']}\n"
        f"링크: {paper['link']}\n"
        f"초록: {paper['summary']}"
    )

    prompt = REVIEW_PROMPT.format(paper_info=paper_info, fulltext=fulltext)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── 이메일 발송 ───────────────────────────────────────────────────────────────

def build_email_body(reviews: list[tuple[dict, str]]) -> str:
    """3편 리뷰를 하나의 이메일 본문으로 조합합니다."""
    today = date.today().strftime("%Y-%m-%d")
    sections = [f"# Today's AI Research Papers ({today})\n"]

    for i, (paper, review) in enumerate(reviews, 1):
        header = (
            f"## [{i}] {paper['title']}\n"
            f"저자: {paper['authors']}  |  발행일: {paper['published']}  |  링크: {paper['link']}\n\n"
        )
        sections.append(header + review)
        if i < len(reviews):
            sections.append("\n\n" + "=" * 60 + "\n\n")

    return "\n".join(sections)


def send_email(body: str) -> None:
    """Gmail SMTP로 이메일을 발송합니다."""
    gmail_user = os.environ["GMAIL_USER"].strip()
    gmail_password = os.environ["GMAIL_APP_PASSWORD"].strip().replace("\xa0", "").replace(" ", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, RECIPIENT_EMAIL, msg.as_string())

    print(f"[OK] 이메일 발송 완료 → {RECIPIENT_EMAIL}")


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    print("=== AI 논문 데일리 리뷰 시작 ===")

    print("[1/3] 트렌딩 논문 수집 중...")
    papers = fetch_trending_papers(NUM_PAPERS)
    for p in papers:
        print(f"  - {p['title']}")

    reviews = []
    for i, paper in enumerate(papers, 1):
        print(f"[2/3] 논문 {i}/{NUM_PAPERS} 처리 중: {paper['title'][:50]}...")

        fulltext = fetch_fulltext(paper["id"])
        review = generate_review(paper, fulltext)
        reviews.append((paper, review))

        # API 레이트 리밋 방지
        if i < NUM_PAPERS:
            time.sleep(3)

    print("[3/3] 이메일 발송 중...")
    body = build_email_body(reviews)
    send_email(body)

    print("=== 완료 ===")


if __name__ == "__main__":
    main()
