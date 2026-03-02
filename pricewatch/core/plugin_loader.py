import importlib
import inspect
import pkgutil

from .plugin_base import BaseShopAdapter


class ReferenceAdapterNotFound(RuntimeError):
    pass


def discover_adapters(package="pricewatch.shops"):
    pkg = importlib.import_module(package)
    adapters = []
    for modinfo in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        module = importlib.import_module(modinfo.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is BaseShopAdapter:
                continue
            if not issubclass(obj, BaseShopAdapter):
                continue
            if obj.__module__ != module.__name__:
                continue
            try:
                adapters.append(obj())
            except TypeError:
                continue
    return adapters


class ShopRegistry:
    def __init__(self, adapters):
        self.adapters = adapters

    def reference_adapter(self):
        for adapter in self.adapters:
            if adapter.is_reference:
                return adapter
        raise ReferenceAdapterNotFound("Reference adapter not found")

    def for_url(self, url):
        for adapter in self.adapters:
            if adapter.match(url):
                return adapter
        return None

