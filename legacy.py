from bs4 import BeautifulSoup
import requests
from difflib import SequenceMatcher
from urllib.parse import urlparse


class LegacyProductScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_products(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.content, "lxml")

            products = []
            domain = urlparse(url).netloc

            for item in soup.find_all(["div", "article", "td"], class_=["product", "item", "good", "товар"]):
                product = self.extract_product_info(item, domain)
                if product:
                    products.append(product)

            if not products:
                for item in soup.find_all("div"):
                    if any(attr in str(item.get("class", [])).lower() for attr in ["product", "item", "catalog"]):
                        product = self.extract_product_info(item, domain)
                        if product:
                            products.append(product)

            return products

        except Exception as exc:
            return {"error": f"Ошибка при парсинге: {str(exc)}"}

    def extract_product_info(self, element, domain):
        try:
            name_elem = element.find(["h2", "h3", "h4", "a", "span"], class_=["name", "title", "product-name"])
            name = name_elem.get_text(strip=True) if name_elem else None

            article_elem = element.find(["span", "div", "p"], class_=["article", "sku", "code", "артикул"])
            article = article_elem.get_text(strip=True) if article_elem else None

            model_elem = element.find(["span", "div", "p"], class_=["model", "модель"])
            model = model_elem.get_text(strip=True) if model_elem else None

            if not article or not name:
                all_text = element.get_text(separator=" ", strip=True)
                if len(all_text) < 500:
                    if not name or len(name) < 5:
                        name = all_text[:100]
                    if not article:
                        article = name[:20] if name else "N/A"

            if name and len(name) > 3:
                return {
                    "article": article or "N/A",
                    "name": name[:200],
                    "model": model or "N/A",
                    "source_domain": domain,
                }
        except Exception:
            pass

        return None


class LegacyProductComparator:
    def __init__(self):
        self.similarity_threshold = 0.6

    def compare_products(self, all_products):
        matched_groups = []
        used_indices = set()

        for i in range(len(all_products)):
            if i in used_indices:
                continue

            group = [all_products[i]]
            used_indices.add(i)

            for j in range(i + 1, len(all_products)):
                if j in used_indices:
                    continue

                if self.is_similar(all_products[i], all_products[j]):
                    group.append(all_products[j])
                    used_indices.add(j)

            if len(group) > 1:
                matched_groups.append(group)
            else:
                matched_groups.append(group)

        similar = [group for group in matched_groups if len(group) > 1]
        unique = [group[0] for group in matched_groups if len(group) == 1]

        return {
            "similar_products": similar,
            "unique_products": unique,
            "total_products": len(all_products),
        }

    def is_similar(self, product1, product2):
        name_similarity = self.get_similarity(
            product1["name"].lower(),
            product2["name"].lower(),
        )

        article_similarity = self.get_similarity(
            product1["article"].lower(),
            product2["article"].lower(),
        )

        if article_similarity > 0.8:
            return True
        if name_similarity > self.similarity_threshold:
            return True
        return False

    def get_similarity(self, str1, str2):
        return SequenceMatcher(None, str1, str2).ratio()


__all__ = ["LegacyProductScraper", "LegacyProductComparator"]

