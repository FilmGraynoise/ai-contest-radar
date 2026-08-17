import json
import os
import re
from typing import Literal, Optional

from google import genai
from pydantic import BaseModel, Field

from utils import looks_ai_related, parse_iso_date, parse_money_to_won

Category = Literal["image", "video", "writing", "music", "other"]
AIRequirement = Literal["required", "allowed", "restricted", "prohibited", "unknown"]

class ContestAnalysis(BaseModel):
    is_creative_contest: bool = Field(
        description="그림/영상/글/음악/콘텐츠 등 창작물을 제출하는 공모전인지"
    )
    ai_relevant: bool = Field(
        description="생성형 AI의 사용 가능/필수/제한/금지 여부가 공고에 직접 언급되거나 AI 창작이 핵심인지"
    )
    ai_requirement: AIRequirement
    categories: list[Category]
    organizer: Optional[str] = None
    deadline: Optional[str] = Field(
        default=None,
        description="접수 마감일. 알 수 있으면 YYYY-MM-DD, 아니면 null"
    )
    prize_text: Optional[str] = None
    total_prize_won: Optional[int] = None
    eligibility: Optional[str] = None
    summary: str = Field(description="한국어 2문장 이내 핵심 요약")
    ai_reason: str = Field(description="AI 활용 가능 여부를 그렇게 판정한 근거를 짧게")
    confidence: float = Field(ge=0, le=1)

SYSTEM_RULES = """너는 한국 공모전 공고를 정형화하는 데이터 분석기다.
반드시 제공된 공고 텍스트에 근거해서만 판단한다.

AI 판정 규칙:
- required: 생성형 AI 사용이 작품 제작 조건 또는 필수 요건
- allowed: 생성형 AI 사용을 명시적으로 허용하나 필수는 아님
- restricted: 일부 AI만 허용, 사용 범위 제한, 사용 사실 표기/증빙 등 조건부
- prohibited: 생성형 AI 사용 금지를 명시
- unknown: 공고만으로 생성형 AI 허용 여부를 알 수 없음

주의:
- 단지 공모전 주제가 'AI 산업/아이디어/기술'이라는 이유만으로 AI 창작 공모전으로 분류하지 않는다.
- 코딩/모델 개발 경진대회는 창작물 공모전이 아니면 is_creative_contest=false.
- categories는 복수 가능.
- 날짜와 금액을 추측하지 않는다.
- 상금 총액이 명확하지 않으면 total_prize_won=null.
"""

def _heuristic_fallback(title: str, body: str) -> ContestAnalysis:
    text = f"{title}\n{body}"
    low = text.lower()

    categories = []
    if any(k in low for k in ["그림", "일러스트", "웹툰", "캐릭터", "포스터", "디자인", "이미지"]):
        categories.append("image")
    if any(k in low for k in ["영상", "숏폼", "영화", "애니메이션", "ucc"]):
        categories.append("video")
    if any(k in low for k in ["글", "문학", "시나리오", "소설", "스토리", "에세이"]):
        categories.append("writing")
    if any(k in low for k in ["음악", "음원", "작곡"]):
        categories.append("music")
    if not categories:
        categories = ["other"]

    requirement = "unknown"
    if re.search(r"(ai|인공지능).{0,20}(금지|불가|허용하지)", low):
        requirement = "prohibited"
    elif re.search(r"(ai|인공지능).{0,20}(필수|반드시|활용하여|활용한)", low):
        requirement = "required"
    elif re.search(r"(ai|인공지능).{0,20}(허용|가능|사용 가능)", low):
        requirement = "allowed"

    # Try to find one obvious deadline / prize string only as fallback.
    deadline_match = re.search(r"(20\d{2}[.\-/년]\s*\d{1,2}[.\-/월]\s*\d{1,2})", text)
    deadline = parse_iso_date(deadline_match.group(1)) if deadline_match else None

    prize_match = re.search(r"((?:총\s*)?상금[^\n]{0,50})", text)
    prize_text = prize_match.group(1).strip() if prize_match else None

    return ContestAnalysis(
        is_creative_contest=True,
        ai_relevant=looks_ai_related(text),
        ai_requirement=requirement,
        categories=categories,
        organizer=None,
        deadline=deadline,
        prize_text=prize_text,
        total_prize_won=parse_money_to_won(prize_text),
        eligibility=None,
        summary="AI 분석 호출에 실패해 키워드 기반 임시 분류로 저장된 항목입니다.",
        ai_reason="Gemini 분석 실패로 자동 판정 정확도가 낮습니다.",
        confidence=0.35,
    )

class GeminiAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)

    def analyze(self, title: str, body: str) -> ContestAnalysis:
        prompt = f"""{SYSTEM_RULES}

[공고 제목]
{title}

[공고 본문]
{body}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": ContestAnalysis.model_json_schema(),
                    "temperature": 0.1,
                },
            )
            data = json.loads(response.text)
            parsed = ContestAnalysis.model_validate(data)

            # Normalize deadline if model emitted a Korean-formatted date.
            parsed.deadline = parse_iso_date(parsed.deadline) or parsed.deadline
            if parsed.deadline and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", parsed.deadline):
                parsed.deadline = None

            return parsed
        except Exception as exc:
            print(f"[WARN] Gemini analysis failed: {exc}")
            return _heuristic_fallback(title, body)
