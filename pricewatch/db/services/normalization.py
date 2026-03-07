from __future__ import annotations

import hashlib
from typing import Tuple

from pricewatch.core.normalize import normalize_title


def normalize_product_name(raw_name: str) -> Tuple[str, str]:
    """Normalize product name and return (normalized, sha256 hash).

    Uses shared normalize_title helper to keep consistency with existing logic.
    """
    normalized = normalize_title(raw_name or "")
    name_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, name_hash

