#!/usr/bin/env python
"""Test caching functionality for safe_get"""

import os
import shutil
import time
from unittest.mock import Mock, patch, MagicMock
from parser import (
    safe_get, _get_cache_path, _is_cache_valid,
    _load_from_cache, _save_to_cache, CACHE_DIR, CACHE_MAX_AGE_DAYS
)

def test_cache_path_generation():
    """Test that cache path is generated correctly"""
    url = "https://example.com/page"
    cache_path = _get_cache_path(url)
    assert cache_path.startswith(CACHE_DIR)
    assert cache_path.endswith('.cache')
    print(f"✓ Cache path generation: {cache_path}")

def test_cache_save_load():
    """Test saving and loading cache"""
    # Clean up first
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

    cache_path = _get_cache_path("https://example.com/test")
    test_content = b"Test content for cache"

    # Save to cache
    _save_to_cache(cache_path, test_content)
    assert os.path.exists(cache_path)
    print(f"✓ Cache saved successfully")

    # Load from cache
    loaded = _load_from_cache(cache_path)
    assert loaded == test_content
    print(f"✓ Cache loaded successfully")

    # Clean up
    shutil.rmtree(CACHE_DIR)

def test_cache_validity():
    """Test cache expiration logic"""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

    cache_path = _get_cache_path("https://example.com/test")
    test_content = b"Test content"

    # Create a valid cache
    _save_to_cache(cache_path, test_content)
    assert _is_cache_valid(cache_path)
    print(f"✓ Fresh cache is valid")

    # Simulate an old cache file by modifying its modification time
    old_time = time.time() - (CACHE_MAX_AGE_DAYS + 1) * 24 * 60 * 60
    os.utime(cache_path, (old_time, old_time))
    assert not _is_cache_valid(cache_path)
    print(f"✓ Old cache (older than {CACHE_MAX_AGE_DAYS} days) is invalid")

    # Clean up
    shutil.rmtree(CACHE_DIR)

def test_safe_get_with_cache():
    """Test safe_get with caching enabled"""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

    # Mock session and response
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html>Cached content</html>"
    mock_response.text = "<html>Cached content</html>"
    mock_response.url = "https://example.com/page"
    mock_response.headers = {'Content-Type': 'text/html'}

    mock_session.request.return_value = mock_response
    mock_session.headers = {}

    # First request should hit the network and cache the response
    with patch('parser.FAST_MODE', True):
        result1 = safe_get(mock_session, "https://example.com/page", use_cache=True)

    assert result1 is not None
    assert result1.status_code == 200
    assert mock_session.request.call_count == 1
    print(f"✓ First request hit network and cached response")

    # Second request should load from cache
    result2 = safe_get(mock_session, "https://example.com/page", use_cache=True)

    assert result2 is not None
    assert result2.status_code == 200
    assert mock_session.request.call_count == 1  # Still 1, no new request
    assert result2.content == b"<html>Cached content</html>"
    print(f"✓ Second request loaded from cache")

    # Clean up
    shutil.rmtree(CACHE_DIR)

def test_safe_get_without_cache():
    """Test safe_get with caching disabled"""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html>Content</html>"
    mock_response.text = "<html>Content</html>"
    mock_response.url = "https://example.com/page"
    mock_response.headers = {'Content-Type': 'text/html'}

    mock_session.request.return_value = mock_response
    mock_session.headers = {}

    with patch('parser.FAST_MODE', True):
        result1 = safe_get(mock_session, "https://example.com/test", use_cache=False)
        result2 = safe_get(mock_session, "https://example.com/test", use_cache=False)

    # Both should hit the network
    assert mock_session.request.call_count == 2
    print(f"✓ With use_cache=False, both requests hit network")

def test_only_status_200_cached():
    """Test that only 200 status codes are cached"""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_response.url = "https://example.com/forbidden"
    mock_response.headers = {}

    mock_session.request.return_value = mock_response
    mock_session.headers = {}

    with patch('parser.FAST_MODE', True):
        result = safe_get(mock_session, "https://example.com/forbidden", use_cache=True)

    assert result is None
    cache_path = _get_cache_path("https://example.com/forbidden")
    assert not os.path.exists(cache_path)
    print(f"✓ 403 status code is not cached")

    # Clean up
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

if __name__ == '__main__':
    print("Running cache functionality tests...\n")

    test_cache_path_generation()
    test_cache_save_load()
    test_cache_validity()
    test_safe_get_with_cache()
    test_safe_get_without_cache()
    test_only_status_200_cached()

    print("\n✓ All tests passed!")

