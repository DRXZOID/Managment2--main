from abc import ABC, abstractmethod
from urllib.parse import urlparse


class BaseShopAdapter(ABC):
    name = ""
    domains = ()
    is_reference = False

    def match(self, url: str) -> bool:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        host = parsed.netloc.lower()
        return any(host == domain or host.endswith(f".{domain}") for domain in self.domains)

    def get_categories(self, client):
        return []

    @abstractmethod
    def scrape_category(self, client, category):
        raise NotImplementedError

    @abstractmethod
    def scrape_url(self, client, url, category=None):
        raise NotImplementedError

