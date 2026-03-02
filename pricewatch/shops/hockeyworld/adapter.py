from pricewatch.core.plugin_base import BaseShopAdapter
from pricewatch.core.generic_adapter import GenericAdapter


class HockeyWorldAdapter(BaseShopAdapter):
    name = "hockeyworld"
    domains = ("hockeyworld.com.ua", "www.hockeyworld.com.ua")

    def scrape_category(self, client, category):
        raise NotImplementedError("HockeyWorld adapter does not support scrape_category")

    def scrape_url(self, client, url, category=None):
        # TODO: move selectors/rules to templates loaded from YAML.
        return GenericAdapter().scrape_url(client, url, category)

