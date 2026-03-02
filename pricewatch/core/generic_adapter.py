from urllib.parse import urlparse

from .plugin_base import BaseShopAdapter
from .pagination import paginate_and_collect
from .category_discovery import find_category_page
from .models import ProductItem


class GenericAdapter(BaseShopAdapter):
    name = "generic"
    domains = ()

    def scrape_category(self, client, category):
        raise NotImplementedError("Generic adapter does not support scrape_category")

    def scrape_url(self, client, url, category=None):
        base = url if url.startswith("http") else "https://" + url
        if category:
            candidate = find_category_page(client, client.session, base, category)
            if candidate and candidate != base:
                print(f"  -> discovered category page on target site: {candidate}")
                base = candidate

        raw = paginate_and_collect(
            client,
            client.session,
            base,
            item_selectors=[],
            name_selectors=[],
            price_selectors=[],
            link_selectors=[],
        )
        print(f"    paginate_and_collect returned {len(raw)} raw items")

        results = []
        for it in raw:
            name = it.get("name", "")
            price = it.get("price", "")
            link = it.get("url", "")
            domain = urlparse(link or base).netloc
            results.append(
                ProductItem(
                    name=name,
                    price_raw=price,
                    url=link,
                    source_site=domain,
                )
            )

        if category:
            key = category.lower()
            before = len(results)
            results = [
                r
                for r in results
                if key in (r.name or "").lower()
                or key in (r.url or "").lower()
            ]
            print(f"    filtered {before} -> {len(results)} items using category '{category}'")

        return results
