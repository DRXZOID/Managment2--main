from urllib.parse import urlparse

from pricewatch.core.generic_adapter import GenericAdapter


class FakeResponse:
    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8') if isinstance(content, str) else content
        self.status_code = status_code


class FakeClient:
    def __init__(self):
        self.session = None

    def safe_get(self, url, session=None):
        # Return different fixtures depending on the host
        parsed = urlparse(url)
        host = parsed.netloc
        if 'example.com' in host:
            html = '''
                <html>
                    <body>
                        <nav>
                            <a href="/catalog/helmets">Helmets</a>
                            <a href="/catalog/sticks">Sticks</a>
                            <a href="/about">About us</a>
                            <a href="https://external.com/shop">External shop</a>
                            <a href="/products/skates">Skates</a>
                        </nav>
                    </body>
                </html>
            '''
            return FakeResponse(html)
        return None


def test_get_categories_returns_local_category_links():
    client = FakeClient()
    adapter = GenericAdapter()
    # set domain so adapter will probe https://example.com
    adapter.domains = ("example.com",)

    cats = adapter.get_categories(client)

    # Expect at least the three local category-like links
    urls = {c['url'] for c in cats}
    names = {c['name'] for c in cats}

    assert any('helmets' in u for u in urls)
    assert any('Sticks' in n or 'Sticks' in n for n in names)
    # external link should be filtered out
    assert not any('external.com' in u for u in urls)


def test_get_categories_returns_empty_for_no_domains():
    client = FakeClient()
    adapter = GenericAdapter()
    adapter.domains = ()
    cats = adapter.get_categories(client)
    assert cats == []
