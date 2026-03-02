from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup


def find_category_page(client, session, base_url, category):
    """Try to locate a category-specific URL on *base_url* site."""
    parsed = urlparse(base_url)
    scheme = parsed.scheme or "https"
    domain = f"{scheme}://{parsed.netloc}"

    try_urls = [base_url]
    if base_url.rstrip("/") != domain.rstrip("/"):
        try_urls.append(domain)

    cat_lower = category.lower()
    for u in try_urls:
        resp = client.safe_get(u, session=session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.content, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(" ", strip=True).lower()
            full = urljoin(domain, href)
            if parsed.netloc not in urlparse(full).netloc:
                continue
            if cat_lower in href.lower() or cat_lower in text:
                return full
    return None

