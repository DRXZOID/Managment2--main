#!/usr/bin/env python
"""
Usage examples for safe_get caching functionality
"""

import os
from http_client import make_default_client

# Example 1: Basic usage with default cache settings
def example_basic_usage():
    """Example 1: Basic caching with defaults"""
    print("Example 1: Basic usage with default cache")
    print("-" * 50)

    client = make_default_client()
    url = "https://example.com"

    # First call - fetches from network and caches
    response = client.safe_get(url)
    if response:
        print(f"First request: {response.status_code}")

    # Second call - loads from cache
    response = client.safe_get(url)
    if response:
        print(f"Second request: {response.status_code} (from cache)")

    print()


# Example 2: Disable cache for specific request
def example_disable_cache():
    """Example 2: Disabling cache for specific request"""
    print("Example 2: Disable cache for specific request")
    print("-" * 50)

    client = make_default_client()
    url = "https://example.com/api/data"

    # Always fetch from network
    response = client.safe_get(url, use_cache=False)
    if response:
        print(f"Request 1: {response.status_code} (from network)")

    response = client.safe_get(url, use_cache=False)
    if response:
        print(f"Request 2: {response.status_code} (from network again)")

    print()


# Example 3: Custom cache directory via environment variable
def example_custom_cache_dir():
    """Example 3: Using custom cache directory"""
    print("Example 3: Custom cache directory")
    print("-" * 50)

    # Set custom cache directory before creating the client
    custom_cache = "/tmp/my_custom_cache"
    os.environ['PARSER_CACHE_DIR'] = custom_cache

    client = make_default_client()

    print(f"Cache directory: {client.cache_dir}")
    print(f"Cache max age: {client.cache_max_age_days} days")

    print()


# Example 4: Custom cache max age via environment variable
def example_custom_cache_age():
    """Example 4: Custom cache expiration time"""
    print("Example 4: Custom cache expiration time")
    print("-" * 50)

    # Set cache max age before creating the client
    os.environ['PARSER_CACHE_MAX_AGE_DAYS'] = '7'

    client = make_default_client()

    print(f"Cache max age: {client.cache_max_age_days} days")
    print("Cache will be invalidated after 7 days instead of default 30")

    print()


# Example 5: Handling multiple requests with mixed cache settings
def example_mixed_cache():
    """Example 5: Mixed cache usage"""
    print("Example 5: Mixed cache usage patterns")
    print("-" * 50)

    client = make_default_client()

    urls = [
        ("https://example.com/page1", True),   # Use cache
        ("https://example.com/api/current", False),  # Don't cache (API endpoint)
        ("https://example.com/page2", True),   # Use cache
    ]

    for url, use_cache in urls:
        cache_mode = "cached" if use_cache else "not cached"
        print(f"Fetching {url} ({cache_mode})")
        # Uncomment to run actual requests:
        # response = client.safe_get(url, use_cache=use_cache)

    print()


# Example 6: Cache efficiency check
def example_cache_efficiency():
    """Example 6: Demonstrating cache efficiency"""
    print("Example 6: Cache efficiency")
    print("-" * 50)

    import time

    client = make_default_client()
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/get",
    ]

    print("Note: This example shows cache efficiency metrics")
    print("Uncomment the safe_get calls below to run with actual network requests")
    print()

    # Example timing (simulated)
    print("Expected behavior:")
    print("  First request:  ~500-2000ms (network + cache save)")
    print("  Second request: ~1-10ms   (cache read)")
    print("  Speedup:        ~50-200x faster")

    # For actual measurement:
    # for url in test_urls:
    #     start = time.time()
    #     r1 = client.safe_get(url, use_cache=True)
    #     time1 = time.time() - start
    #
    #     start = time.time()
    #     r2 = client.safe_get(url, use_cache=True)
    #     time2 = time.time() - start
    #
    #     print(f"\n{url}")
    #     print(f"  Network:  {time1*1000:.1f}ms")
    #     print(f"  Cached:   {time2*1000:.1f}ms")
    #     print(f"  Speedup:  {time1/time2:.1f}x")

    print()


# Example 7: Environment variable configuration
def example_env_config():
    """Example 7: Environment variable configuration"""
    print("Example 7: Complete environment configuration")
    print("-" * 50)

    print("To use custom cache settings, set these environment variables:")
    print()
    print("  # Custom cache directory")
    print("  export PARSER_CACHE_DIR='/path/to/cache'")
    print()
    print("  # Custom cache expiration (in days)")
    print("  export PARSER_CACHE_MAX_AGE_DAYS='60'")
    print()
    print("  # Then run your script:")
    print("  python your_script.py")
    print()
    print("Or set inline:")
    print("  PARSER_CACHE_DIR=/tmp/cache python your_script.py")

    print()


if __name__ == '__main__':
    print("=" * 50)
    print("safe_get Cache Usage Examples")
    print("=" * 50)
    print()

    example_basic_usage()
    example_disable_cache()
    example_custom_cache_dir()
    example_custom_cache_age()
    example_mixed_cache()
    example_cache_efficiency()
    example_env_config()

    print("=" * 50)
    print("For more information, see CACHING.md")
    print("=" * 50)

