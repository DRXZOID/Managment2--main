from .plugin_loader import ShopRegistry, discover_adapters


_registry = None


def get_registry():
    global _registry
    if _registry is None:
        _registry = ShopRegistry(discover_adapters())
    return _registry

