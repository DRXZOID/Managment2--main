from pricewatch.core.registry import get_registry
from pricewatch.core.reference_service import ReferenceCatalogBuilder
from pricewatch.core.generic_adapter import GenericAdapter
from pricewatch.core.normalize import product_exists_on_main, parse_price
from pricewatch.core.models import ProductItem


registry = get_registry()


def _item_to_dict(item: ProductItem):
    if item.parsed_price:
        price_value = item.parsed_price.value
        currency = item.parsed_price.currency
    else:
        price_value, currency = parse_price(item.price_raw)
    return {
        "name": item.name,
        "price": price_value,
        "currency": currency,
        "url": item.url,
        "source_site": item.source_site,
    }


def get_prohockey_categories(client):
    reference = registry.reference_adapter()
    return reference.get_categories(client)


def fetch_main_site_products(client, categories=None):
    """Return list of products from the reference site (prohockey) suitable
    for matching. Each item is dict with name, price, currency, url, source_site.

    If *categories* is ``None`` the set of available categories is pulled
    dynamically from the prohockey homepage via :func:`get_prohockey_categories`.
    """
    reference = registry.reference_adapter()
    builder = ReferenceCatalogBuilder(reference, client)
    items = builder.build(categories)
    return [_item_to_dict(item) for item in items]


def fetch_other_site_products(client, url, category=None):
    """Generic fetch for any other site URL. Returns list of product dicts."""
    print(f"fetch_other_site_products: {url} (category={category})")
    base = url if url.startswith("http") else "https://" + url

    adapter = registry.for_url(base) or GenericAdapter()
    results = adapter.scrape_url(client, base, category=category)
    return [_item_to_dict(item) for item in results]


__all__ = [
    "fetch_main_site_products",
    "fetch_other_site_products",
    "product_exists_on_main",
    "get_prohockey_categories",
]
