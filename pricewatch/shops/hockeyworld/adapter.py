from urllib.parse import urlparse, urljoin

from pricewatch.core.plugin_base import BaseShopAdapter
from pricewatch.core.models import ProductItem
from bs4 import BeautifulSoup


class HockeyWorldAdapter(BaseShopAdapter):
    name = "hockeyworld"
    domains = ("www.hockeyworld.com.ua", "hockeyworld.com.ua")

    def scrape_category(self, client, category):
        raise NotImplementedError("HockeyWorld adapter does not support scrape_category")

    def scrape_url(self, client, url, category=None):
        """Scrape products from the given URL on hockeyworld site.

        Each product is expected inside <div class="product">.
        - price: inside <div class="PricesalesPrice"> (text)
        - description/name: inside <div class="product-s-desc"> (text)
        - product link: inside <div class="product-addtocart"> (first <a href> or data-href)
        """
        base = url if url.startswith('http') else 'https://' + url
        print(f"HockeyWorldAdapter.scrape_url: fetching {base} (category={category})")
        resp = client.safe_get(base, session=client.session)
        if not resp:
            print(f"  -> no response from {base}")
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        items = []
        product_nodes = soup.find_all('div', class_='product')
        print(f"  -> found {len(product_nodes)} product nodes")

        for node in product_nodes:
            # extract name/description
            name_node = node.find('div', class_='product-s-desc')
            name = name_node.get_text(' ', strip=True) if name_node else ''

            # extract price (raw)
            price_node = node.find('div', class_='PricesalesPrice')
            price = price_node.get_text(' ', strip=True) if price_node else ''

            # extract link: prefer anchor inside product-addtocart
            link = None
            add_node = node.find('div', class_='product-addtocart')
            if add_node:
                a = add_node.find('a', href=True)
                if a:
                    link = a['href']
                else:
                    # fallback: look for any element with data-href or onclick
                    data_href = add_node.get('data-href') or add_node.get('data-url')
                    if data_href:
                        link = data_href
                    else:
                        # try to find button with onclick containing URL
                        btn = add_node.find(attrs={'onclick': True})
                        if btn:
                            onclick = btn.get('onclick')
                            # try to extract a quoted URL
                            import re

                            m = re.search(r"['\"](https?://[^'\"]+)['\"]", onclick)
                            if m:
                                link = m.group(1)

            # if still no link, try any <a> inside the product node
            if not link:
                a_any = node.find('a', href=True)
                if a_any:
                    link = a_any['href']

            # build absolute link
            full_link = None
            if link:
                full_link = urljoin(base, link)
            else:
                full_link = base

            domain = urlparse(full_link).netloc

            item = ProductItem(
                name=name,
                price_raw=price,
                url=full_link,
                source_site=domain,
            )
            items.append(item)

        # Optionally filter by category keyword if provided (keep existing behaviour)
        if category:
            key = category.lower()
            before = len(items)
            items = [it for it in items if key in (it.name or '').lower() or key in (it.url or '').lower()]
            print(f"  -> filtered {before} -> {len(items)} items using category '{category}'")

        print(f"  -> returning {len(items)} items")
        return items

    def get_categories(self, client):
        host = next(iter(self.domains), None)
        if not host:
            return []
        base = f"http://{host}"

        try:
            resp = client.safe_get(base, session=client.session)
        except Exception as exc:
            print(f"get_categories: failed to fetch {base}: {exc}")
            return []

        if not resp:
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        out = []
        # Only look for links inside <div class="menu_round"> blocks
        containers = soup.find_all('div', class_='menu_round')
        if not containers:
            print("  -> no .menu_round blocks found on the page")
            return []

        for block in containers:
            for a in block.find_all('a', href=True):
                href = a['href']
                if not href.startswith('/kategorii-tovarov/'):
                    continue
                span = a.find('span')
                name = span.get_text(strip=True) if span else a.get_text(" ", strip=True)
                full = urljoin(base, href)
                # ensure same domain
                if urlparse(full).netloc != urlparse(base).netloc:
                    continue
                print(f"  -> discovered hockeyworld category: {name} -> {full}")
                out.append({'name': name, 'url': full})

        return out
