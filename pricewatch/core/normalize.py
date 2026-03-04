import re
from typing import Optional, Tuple

try:
    from rapidfuzz import fuzz
    _ratio = fuzz.ratio
except Exception:
    from difflib import SequenceMatcher

    def _ratio(a, b):
        return SequenceMatcher(None, a, b).ratio() * 100


MAIN_NORMALIZED = []


def parse_price(price_str):
    if not price_str:
        return "", ""
    m = re.search(r"([\d\s,.]+)\s*([^\d\s]+)", price_str)
    if m:
        value = m.group(1).strip()
        curr = m.group(2).strip()
        return value, curr
    return price_str.strip(), ""


def parse_price_value(price_str: str) -> Tuple[Optional[float], str]:
    if not price_str:
        return None, ""
    value_str, currency = parse_price(price_str)
    if not value_str:
        return None, currency or ""

    s = value_str.replace(' ', '').replace('\u00A0', '').replace(',', '.')
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None, currency or ""
    num_s = m.group(0)
    try:
        return float(num_s), currency or ""
    except Exception:
        return None, currency or ""


def normalize_title(title: str) -> str:
    t = title.lower()
    t = re.sub(r"\([^)]*\)", "", t)
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def product_exists_on_main(title: str, threshold: float = 85.0) -> bool:
    norm = normalize_title(title)
    for existing in MAIN_NORMALIZED:
        if norm == existing:
            return True
        score = _ratio(norm, existing)
        if score >= threshold:
            return True
    return False
