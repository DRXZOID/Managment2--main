from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParsedPrice:
    value: str
    currency: str


@dataclass(frozen=True)
class ProductItem:
    name: str
    price_raw: str
    url: str
    source_site: str
    parsed_price: Optional[ParsedPrice] = None

