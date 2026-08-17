import hashlib
import re
from datetime import date, datetime
from typing import Optional

AI_KEYWORDS = [
    "생성형 ai", "생성형ai", "인공지능", " ai ", "a.i.", "chatgpt", "gpt",
    "gemini", "midjourney", "미드저니", "stable diffusion", "스테이블 디퓨전",
    "runway", "kling", "클링", "suno", "수노", "ai 활용", "ai활용", "ai 콘텐츠",
    "ai콘텐츠", "ai 영상", "ai영상", "ai 이미지", "ai이미지", "ai 창작", "ai창작"
]

CREATIVE_KEYWORDS = [
    "영상", "숏폼", "영화", "애니메이션", "그림", "일러스트", "웹툰", "캐릭터",
    "포스터", "디자인", "사진", "글", "문학", "시", "소설", "시나리오", "스토리",
    "콘텐츠", "음악", "음원", "작곡"
]

def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()

def normalize_for_fingerprint(value: str) -> str:
    value = normalize_space(value).lower()
    return re.sub(r"[^0-9a-z가-힣]", "", value)

def make_fingerprint(title: str, organizer: str = "", deadline: str = "") -> str:
    raw = "|".join([
        normalize_for_fingerprint(title),
        normalize_for_fingerprint(organizer),
        normalize_for_fingerprint(deadline),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def looks_ai_related(text: str) -> bool:
    low = f" {normalize_space(text).lower()} "
    return any(k in low for k in AI_KEYWORDS)

def looks_creative(text: str) -> bool:
    low = normalize_space(text).lower()
    return any(k in low for k in CREATIVE_KEYWORDS)

def parse_iso_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()

    # YYYY-MM-DD / YYYY.MM.DD / YYYY/MM/DD
    m = re.search(r"(20\d{2})[.\-/년\s]+(\d{1,2})[.\-/월\s]+(\d{1,2})", value)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None

    return None

def parse_money_to_won(value: Optional[str]) -> Optional[int]:
    """Best-effort. Returns total prize estimate in KRW when a single amount is clear."""
    if not value:
        return None
    text = value.replace(",", "").replace(" ", "")

    # 억
    m = re.search(r"(\d+(?:\.\d+)?)억", text)
    if m:
        return int(float(m.group(1)) * 100_000_000)

    # 천만원 / 백만원 / 만원
    m = re.search(r"(\d+(?:\.\d+)?)천만원", text)
    if m:
        return int(float(m.group(1)) * 10_000_000)

    m = re.search(r"(\d+(?:\.\d+)?)백만원", text)
    if m:
        return int(float(m.group(1)) * 1_000_000)

    m = re.search(r"(\d+(?:\.\d+)?)만원", text)
    if m:
        return int(float(m.group(1)) * 10_000)

    m = re.search(r"(\d{5,})원", text)
    if m:
        return int(m.group(1))

    return None
