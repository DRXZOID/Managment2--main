from pricewatch.core.plugin_base import BaseShopAdapter


class DummyShopOneAdapter(BaseShopAdapter):
    name = "dummy_one"
    domains = ("dummy-one.test",)

    def scrape_category(self, client, category):
        raise NotImplementedError

    def scrape_url(self, client, url, category=None):
        raise NotImplementedError
