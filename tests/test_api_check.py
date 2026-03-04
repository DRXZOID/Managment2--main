from app import app, registry
from pricewatch.core.models import ProductItem


def make_product(name, price_raw, url, source_site):
    return ProductItem(name=name, price_raw=price_raw, url=url, source_site=source_site)


def test_check_missing_happy(monkeypatch):
    # prepare reference products: one item matching name 'Test product'
    ref = [make_product('Test product', '1000 UAH', 'https://prohockey/1', 'prohockey.com.ua')]

    # monkeypatch ReferenceCatalogBuilder.build to return our ref list
    from pricewatch.core.reference_service import ReferenceCatalogBuilder

    def fake_build(self, categories=None):
        return ref

    monkeypatch.setattr(ReferenceCatalogBuilder, 'build', fake_build)

    # prepare adapter that will be returned by registry.for_url
    class DummyAdapter:
        name = 'dummy'

        def scrape_url(self, client, url, category=None):
            return [make_product('Test product', '1200 UAH', url, 'dummy-site')]

    # monkeypatch registry.for_url to return DummyAdapter instance
    monkeypatch.setattr(registry, 'for_url', lambda url: DummyAdapter())

    client = app.test_client()
    resp = client.post('/api/check', json={'urls': ['dummy-site'], 'category': ''})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'missing' in data
    assert len(data['missing']) == 1
    entry = data['missing'][0]
    assert entry['status'] == 0  # ref_price 1000 <= 1200 test
    assert entry['ref'] is not None
    assert entry['ref']['price'] == 1000.0


def test_check_missing_currency_mismatch(monkeypatch):
    ref = [make_product('Test product', '1000 USD', 'https://prohockey/1', 'prohockey.com.ua')]

    from pricewatch.core.reference_service import ReferenceCatalogBuilder

    def fake_build(self, categories=None):
        return ref

    monkeypatch.setattr(ReferenceCatalogBuilder, 'build', fake_build)

    class DummyAdapter:
        name = 'dummy'

        def scrape_url(self, client, url, category=None):
            return [make_product('Test product', '1200 UAH', url, 'dummy-site')]

    monkeypatch.setattr(registry, 'for_url', lambda url: DummyAdapter())

    client = app.test_client()
    resp = client.post('/api/check', json={'urls': ['dummy-site'], 'category': ''})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['missing'][0]['status'] == 2
    assert data['missing'][0]['status_reason'] == 'currency_mismatch'


def test_check_missing_invalid_price(monkeypatch):
    # reference with invalid price string
    ref = [make_product('Test product', 'n/a', 'https://prohockey/1', 'prohockey.com.ua')]

    from pricewatch.core.reference_service import ReferenceCatalogBuilder

    def fake_build(self, categories=None):
        return ref

    monkeypatch.setattr(ReferenceCatalogBuilder, 'build', fake_build)

    class DummyAdapter:
        name = 'dummy'

        def scrape_url(self, client, url, category=None):
            return [make_product('Test product', '1200 UAH', url, 'dummy-site')]

    monkeypatch.setattr(registry, 'for_url', lambda url: DummyAdapter())

    client = app.test_client()
    resp = client.post('/api/check', json={'urls': ['dummy-site'], 'category': ''})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['missing'][0]['status'] == 2
    assert data['missing'][0]['status_reason'] == 'invalid_ref_price'

