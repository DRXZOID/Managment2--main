import json
from urllib.parse import urljoin


def extract_text(el):
    return el.get_text(strip=True) if el else ""


def extract_products_from_json(obj, base_url):
    """Recursively search a JSON-like object for product lists."""
    results = []
    if isinstance(obj, dict):
        for _, v in obj.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                sample = v[0]
                if any(key in sample for key in ("name", "title", "price", "url", "link")):
                    for item in v:
                        name = item.get("name") or item.get("title", "")
                        price = item.get("price", "")
                        url = normalize_link(base_url, item.get("url") or item.get("link") or "")
                        results.append({"name": name, "price": price, "url": url})
                    return results
            sub = extract_products_from_json(v, base_url)
            if sub:
                results.extend(sub)
    elif isinstance(obj, list):
        for el in obj:
            sub = extract_products_from_json(el, base_url)
            if sub:
                results.extend(sub)
    return results


def scan_for_json_in_html(soup, base_url):
    """Look inside <script> tags for inline JSON containing product data."""

    def find_json_strings(text):
        results = []
        stack = []
        start = None
        for i, ch in enumerate(text):
            if ch in "{[":
                if not stack:
                    start = i
                stack.append(ch)
            elif ch in "]}" and stack:
                stack.pop()
                if not stack and start is not None:
                    results.append(text[start:i + 1])
                    start = None
        return results

    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        if not text:
            continue
        for candidate in find_json_strings(text):
            try:
                payload = json.loads(candidate)
                products = extract_products_from_json(payload, base_url)
                if products:
                    return products
            except Exception:
                pass
    return None


def find_first(soup, selectors):
    for sel in selectors:
        elems = soup.select(sel)
        if elems:
            return elems
    return []


def normalize_link(base, link):
    if not link:
        return ""
    return urljoin(base, link)

