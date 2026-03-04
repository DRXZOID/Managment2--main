from pricewatch.core.plugin_base import BaseShopAdapter


class DummyShopTwoAdapter(BaseShopAdapter):
    name = "dummy_two"
    domains = ("dummy-two.test",)

    def scrape_category(self, client, category):
        raise NotImplementedError

    def scrape_url(self, client, url, category=None):
        raise NotImplementedError

