from urllib.parse import urlparse

from pricewatch.shops.hockeyworld.adapter import HockeyWorldAdapter


class FakeResponse:
    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8') if isinstance(content, str) else content
        self.status_code = status_code


class FakeClient:
    def __init__(self):
        self.session = None

    def safe_get(self, url, session=None):
        parsed = urlparse(url)
        host = parsed.netloc
        if 'hockeyworld.com.ua' in host:
            html = '''
                <html>
                    <body>
                        <div class="menu_round">
                            <ul>
                                <li><a href="/kategorii-tovarov/helmets"><span>Helmets</span></a></li>
                                <li><a href="/kategorii-tovarov/sticks"><span>Hockey Sticks</span></a></li>
                                <li><a href="/other/link"><span>Other</span></a></li>
                                <li><a href="https://external.com/kategorii-tovarov/x"><span>External</span></a></li>
                            </ul>
                        </div>
                    </body>
                </html>
            '''
            return FakeResponse(html)
        return None


def test_hockeyworld_get_categories():
    client = FakeClient()
    adapter = HockeyWorldAdapter()
    cats = adapter.get_categories(client)

    assert isinstance(cats, list)
    urls = {c['url'] for c in cats}
    names = {c['name'] for c in cats}

    assert any('/kategorii-tovarov/helmets' in u for u in urls)
    assert any('Helmets' in n for n in names)
    assert any('/kategorii-tovarov/sticks' in u for u in urls)
    assert any('Hockey Sticks' in n for n in names)
    # should not include /other/link or external domain
    assert not any('/other/link' in u for u in urls)
    assert not any('external.com' in u for u in urls)
