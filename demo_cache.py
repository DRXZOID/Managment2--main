#!/usr/bin/env python
"""Example demonstrating cache usage with safe_get"""

import time
import os
import shutil
from parser import create_session, safe_get, CACHE_DIR

def demo_cache_usage():
    """Demonstrate cache functionality"""

    # Clean up cache from previous runs
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

    session = create_session()

    # Test URL (using httpbin for testing)
    test_url = "https://httpbin.org/html"

    print("=" * 60)
    print("Cache Demo: Fetching the same URL twice")
    print("=" * 60)

    # First request - should hit the network
    print(f"\n1. First request to {test_url}")
    print("   (should fetch from network and cache)")
    start = time.time()
    response1 = safe_get(session, test_url, use_cache=True)
    elapsed1 = time.time() - start

    if response1:
        print(f"   Status: {response1.status_code}")
        print(f"   Size: {len(response1.content)} bytes")
        print(f"   Time: {elapsed1:.3f}s (includes network delay)")

    # Small delay to ensure times are different
    time.sleep(1)

    # Second request - should load from cache
    print(f"\n2. Second request to {test_url}")
    print("   (should load from cache)")
    start = time.time()
    response2 = safe_get(session, test_url, use_cache=True)
    elapsed2 = time.time() - start

    if response2:
        print(f"   Status: {response2.status_code}")
        print(f"   Size: {len(response2.content)} bytes")
        print(f"   Time: {elapsed2:.3f}s (from cache, much faster)")

    # Verify cache contents match
    if response1 and response2:
        if response1.content == response2.content:
            print(f"\n✓ Content matches between network and cache")
        else:
            print(f"\n✗ Content mismatch!")

    # Show speedup
    if elapsed1 > 0:
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else float('inf')
        print(f"\n✓ Speedup: {speedup:.1f}x faster from cache")

    # Third request with caching disabled
    print(f"\n3. Third request to {test_url}")
    print("   (caching disabled - should fetch from network again)")
    start = time.time()
    response3 = safe_get(session, test_url, use_cache=False)
    elapsed3 = time.time() - start

    if response3:
        print(f"   Status: {response3.status_code}")
        print(f"   Time: {elapsed3:.3f}s (network request)")

    print("\n" + "=" * 60)
    print(f"Cache directory: {os.path.abspath(CACHE_DIR)}")
    if os.path.exists(CACHE_DIR):
        files = os.listdir(CACHE_DIR)
        print(f"Cached files: {len(files)}")
        for f in files:
            size = os.path.getsize(os.path.join(CACHE_DIR, f))
            print(f"  - {f} ({size} bytes)")
    print("=" * 60)

    # Cleanup
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print(f"\nCleaned up cache directory")

if __name__ == '__main__':
    try:
        demo_cache_usage()
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This demo requires internet connection.")
        print("Running with httpbin.org for testing purposes.")

