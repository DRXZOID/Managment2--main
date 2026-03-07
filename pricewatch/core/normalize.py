import re
from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process

# ----------------------------
# Helpers: parsing/normalizing
# ----------------------------

BRANDS = {
    "bauer": "BAUER",
    "ccm": "CCM",
    "true": "TRUE",
    "graf": "GRAF",
    "jackson": "JACKSON",
    "edea": "EDEA",
    "tour": "TOUR",
    "warrior": "WARRIOR",
    "mission": "MISSION",
}

LEVEL_RULES = [
    (re.compile(r"\b(sr|senior|взросл|доросл)\b", re.I), "SR"),
    (re.compile(r"\b(int|intermediate|intermidiate|подрост|підліт)\b", re.I), "INT"),
    (re.compile(r"\b(jr|junior|юниор|юніор)\b", re.I), "JR"),
    (re.compile(r"\b(yth|youth|детск|дитяч)\b", re.I), "YTH"),
]

NOISE_RX = re.compile(
    r"\b("
    r"купити|купить|новинка|акція|знижка|хіт|top|sale|"
    r"official|гарантія|подарунок|уцінка|комплект"
    r")\b",
    re.I,
)

MAIN_NORMALIZED = []

def _field(item: Any, key: str, default: Any = None) -> Any:
    if item is None:
        return default
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)

def _get_title(item: Any) -> str:
    return str(_field(item, "name") or _field(item, "title") or "").strip()

def _normalize_title(s: str) -> str:
    s = s.lower()
    s = s.replace("—", " ").replace("-", " ").replace("/", " ").replace("+", " ")
    s = re.sub(r"[^\w\s\.]", " ", s, flags=re.U)
    s = re.sub(r"\s+", " ", s).strip()
    s = NOISE_RX.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _extract_brand(title: str) -> Optional[str]:
    t = title.lower()
    for k, v in BRANDS.items():
        if re.search(rf"\b{k}\b", t):
            return v
    return None

def _extract_level(title: str) -> Optional[str]:
    for rx, lvl in LEVEL_RULES:
        if rx.search(title):
            return lvl
    return None

def _extract_tokens(title: str) -> Tuple[str, ...]:
    t = title.upper()
    tokens = set()

    # TF9, FT8, FT860, M40, X5, XF70...
    for m in re.findall(r"\b[A-Z]{1,3}\d{1,4}[A-Z]?\b", t):
        tokens.add(m)

    # series tokens (helpful even outside skates)
    for series in [
        "JETSPEED", "TACKS", "RIBCOR", "VAPOR", "SUPREME",
        "CATALYST", "HZRDUS", "NEXT", "XF", "MACH", "HYPERLITE", "SHADOW"
    ]:
        if re.search(rf"\b{series}\b", t):
            tokens.add(series)

    # Hyperlite 2 => HYPERLITE2
    m = re.search(r"\b(HYPERLITE|MACH|SHADOW)\s*(\d)\b", t)
    if m:
        tokens.add(f"{m.group(1)}{m.group(2)}")

    # 3X PRO => 3XPRO
    m = re.search(r"\b(\dX)\s*PRO\b", t)
    if m:
        tokens.add(f"{m.group(1)}PRO")

    return tuple(sorted(tokens))

def _parse_price_uah(price_raw: Any) -> Optional[int]:
    if price_raw is None:
        return None
    s = str(price_raw)
    m = re.search(r"(\d[\d\s]*)\s*грн", s, re.I) or re.search(r"(\d[\d\s]*)грн", s, re.I)
    if not m:
        return None
    return int(re.sub(r"\s+", "", m.group(1)))

def _prep(items: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        title = _get_title(it)
        norm = _normalize_title(title)
        out.append({
            "_src": source,
            "_raw": it,  # keep original dict
            "_title": title,
            "_norm": norm,
            "_price_uah": _parse_price_uah(_field(it, "price_raw")),
            "_url": _field(it, "url"),
            "_brand": _extract_brand(title),
            "_level": _extract_level(title),
            "_tokens": _extract_tokens(title),
        })
    return out

def _pair_score(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    # hard brand block only if both known
    if a["_brand"] and b["_brand"] and a["_brand"] != b["_brand"]:
        return -1e9

    base = fuzz.token_set_ratio(a["_norm"], b["_norm"])  # 0..100

    inter = set(a["_tokens"]).intersection(b["_tokens"])
    bonus = 0.0
    if inter:
        strong = [t for t in inter if any(ch.isdigit() for ch in t)]
        bonus += 8.0 * len(strong) + 3.0 * (len(inter) - len(strong))

    penalty = 0.0
    if a["_level"] and b["_level"] and a["_level"] != b["_level"]:
        penalty += 25.0

    return base + bonus - penalty

def _color_for_matched(main_price: Optional[int], other_price: Optional[int]) -> str:
    # only compare if both prices are known
    if main_price is None or other_price is None:
        return "none"
    if main_price < other_price:
        return "green"
    if main_price > other_price:
        return "yellow"
    return "none"

# ----------------------------
# Public API
# ----------------------------

def heuristic_match(
    reference_items: List[Dict[str, Any]],
    target_items: List[Dict[str, Any]],
    *,
    top_k: int = 25,
    min_score: float = 78.0,
    min_gap: float = 6.0,
) -> List[Dict[str, Any]]:
    """Match two lists of product dicts using brand/token/fuzzy heuristics.

    Each item dict must have a ``name`` (or ``title``) key.  Optional keys
    ``price_raw`` and ``url`` are used for price comparison and URL storage.

    Returns a flat list of result dicts, each with:
      - ``status``:     ``"matched"`` | ``"ambiguous"`` | ``"no_match"``
      - ``color``:      ``"green"`` | ``"yellow"`` | ``"none"`` | ``"blue"`` | ``"red"``
      - ``main``:       original reference item dict (or ``None``)
      - ``other``:      original target item dict (or ``None``)
      - ``score``:      best fuzzy score (float, when computed)
      - ``gap``:        score gap to second-best candidate (float, when computed)
      - ``candidates``: top-3 ambiguous candidates (only when ``status=="ambiguous"``)

    ``min_score`` and ``min_gap`` use the canonical defaults (78.0 / 6.0) and
    should not be changed without re-testing matching quality.
    """
    main = _prep(reference_items, "main")
    other = _prep(target_items, "other")

    other_by_brand: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for b in other:
        other_by_brand.setdefault(b["_brand"], []).append(b)
        other_by_brand.setdefault(None, []).append(b)

    other_index_map = {id(obj): idx for idx, obj in enumerate(other)}
    used_other_idx: set = set()
    results: List[Dict[str, Any]] = []

    for a in main:
        pool = other_by_brand.get(a["_brand"], other_by_brand.get(None, []))
        if not pool:
            results.append({"status": "no_match", "color": "blue", "main": a["_raw"], "other": None})
            continue

        norms = [b["_norm"] for b in pool]
        cands = process.extract(a["_norm"], norms, scorer=fuzz.token_set_ratio, limit=top_k)

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for _, _, idx in cands:
            b = pool[idx]
            scored.append((_pair_score(a, b), b))
        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            results.append({"status": "no_match", "color": "blue", "main": a["_raw"], "other": None})
            continue

        best_score, best = scored[0]
        second_score = scored[1][0] if len(scored) > 1 else -1e9
        gap = best_score - second_score

        if best_score < min_score:
            results.append({
                "status": "no_match", "color": "blue",
                "main": a["_raw"], "other": None,
                "score": float(best_score), "gap": float(gap),
            })
            continue

        if gap < min_gap:
            results.append({
                "status": "ambiguous", "color": "blue",
                "main": a["_raw"], "other": None,
                "score": float(best_score), "gap": float(gap),
                "candidates": [{"score": float(s), "item": b["_raw"]} for s, b in scored[:3]],
            })
            results.append({
                "status": "ambiguous", "color": "red",
                "main": None, "other": best["_raw"],
                "score": float(best_score), "gap": float(gap),
            })
            continue

        b_idx = other_index_map.get(id(best))
        if b_idx is not None:
            used_other_idx.add(b_idx)
        results.append({
            "status": "matched",
            "color": _color_for_matched(a["_price_uah"], best["_price_uah"]),
            "main": a["_raw"], "other": best["_raw"],
            "score": float(best_score), "gap": float(gap),
        })

    for idx, b in enumerate(other):
        if idx not in used_other_idx:
            results.append({"status": "no_match", "color": "red", "main": None, "other": b["_raw"]})

    return results


def product_exists_on_main(
    main_list_or_title,
    other_list: List[Dict[str, Any]] | None = None,
    *,
    top_k: int = 25,
    min_score: float = 78.0,
    min_gap: float = 6.0,
) -> List[Dict[str, Any]]:
    """
    Dual-purpose helper:
    - If called with a single string argument (title), returns bool indicating whether
      the normalized title exists in MAIN_NORMALIZED. This keeps compatibility with
      legacy convenience callers/tests.
    - If called with two lists (main_list, other_list) behaves as before and returns
      a list of result dicts describing matches/no-matches.
    """
    # Convenience single-title check: product_exists_on_main(title)
    if other_list is None and isinstance(main_list_or_title, str):
        # fuzzy match against MAIN_NORMALIZED entries
        title_norm = normalize_title(main_list_or_title)
        for m in MAIN_NORMALIZED:
            try:
                score = fuzz.token_set_ratio(title_norm, m)
            except Exception:
                score = 0.0
            if score >= min_score:
                return True
        return False

    # Backward-compatible full matcher: delegates to heuristic_match
    return heuristic_match(
        main_list_or_title,
        other_list or [],
        top_k=top_k,
        min_score=min_score,
        min_gap=min_gap,
    )

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

