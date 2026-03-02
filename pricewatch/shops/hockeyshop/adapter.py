from pricewatch.core.plugin_base import BaseShopAdapter
from pricewatch.core.generic_adapter import GenericAdapter


class HockeyShopAdapter(BaseShopAdapter):
    name = "hockeyshop"
    domains = ("hockeyshop.com.ua", "www.hockeyshop.com.ua")

    def scrape_category(self, client, category):
        raise NotImplementedError("HockeyShop adapter does not support scrape_category")

    def scrape_url(self, client, url, category=None):
        # TODO: move selectors/rules to templates loaded from YAML.
        return GenericAdapter().scrape_url(client, url, category)

