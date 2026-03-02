from urllib.parse import urlparse

from bs4 import BeautifulSoup

from pricewatch.core.plugin_base import BaseShopAdapter
from pricewatch.core.pagination import paginate_and_collect
from pricewatch.core.category_discovery import find_category_page
from pricewatch.core.models import ProductItem


class ProHockeyAdapter(BaseShopAdapter):
    name = "prohockey"
    domains = ("prohockey.com.ua", "www.prohockey.com.ua")
    is_reference = True

    def get_categories(self, client):
        base = "https://prohockey.com.ua"
        resp = client.safe_get(base, session=client.session)
        if not resp:
            return []
        soup = BeautifulSoup(resp.content, "html.parser")
        cats = set()
        for a in soup.select("a[href]"):
            href = a["href"]
            if "/catalog/" in href:
                parsed = urlparse(href)
                path = parsed.path
                parts = path.split("/catalog/")
                if len(parts) > 1:
                    slug = parts[1].strip("/")
                    if slug:
                        cats.add(slug)
        return sorted(cats)

    def scrape_category(self, client, category):
        # TODO: move selectors/rules to templates loaded from YAML.
        base = f"https://prohockey.com.ua/catalog/{category}"
        if category:
            found = find_category_page(client, client.session, "https://prohockey.com.ua", category)
            if found and found != base:
                print(f"  -> using discovered reference category page: {found}")
                base = found

        item_selectors = [
            'div[class*="product"][class*="item"]',
            "div.card",
            'div.row > div[class*="col"] > div[class*="product"]',
            "article.product",
            "div[data-product-id]",
            "div.catalog-item",
            "div.product",
            "div.item",
            "div.tz-item",
            "li.product",
            "div.catalog__item",
            ".catalog-card",
            ".product-list-item",
        ]

        name_selectors = [
            "a.product-title",
            "a.catalog-item__title",
            "h3 a",
            "h2 a",
            ".title a",
            ".product-name a",
            "h1",
            "h2",
            "h3",
            "h4",
            "a",
        ]

        price_selectors = [
            ".price .value",
            ".price",
            ".catalog-item__price",
            ".woocommerce-Price-amount",
            ".tov_price",
            ".product-price",
            '[class*="price"]',
        ]

        link_selectors = [
            "a.product-title",
            ".catalog-item__title a",
            "h3 a",
            "a",
        ]

        raw = paginate_and_collect(
            client,
            client.session,
            base,
            item_selectors,
            name_selectors,
            price_selectors,
            link_selectors,
        )
        results = []
        for r in raw:
            results.append(
                ProductItem(
                    name=r.get("name", ""),
                    price_raw=r.get("price", ""),
                    url=r.get("url", ""),
                    source_site="prohockey.com.ua",
                )
            )
        return results

    def scrape_url(self, client, url, category=None):
        raise NotImplementedError("Reference adapter uses scrape_category")

