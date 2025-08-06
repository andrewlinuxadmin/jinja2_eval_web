#!/usr/bin/env python3

import urllib.request
import urllib.parse

def test_endpoint(url, expected_status):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode()
            print(f"URL: {url}")
            print(f"Status: {status} (expected: {expected_status})")
            print(f"Content: {content[:100]}...")
            print("-" * 50)
            return status == expected_status
    except urllib.error.HTTPError as e:
        print(f"URL: {url}")
        print(f"Status: {e.code} (expected: {expected_status})")
        print(f"Error: {e.reason}")
        print("-" * 50)
        return e.code == expected_status
    except Exception as e:
        print(f"URL: {url}")
        print(f"Error: {e}")
        print("-" * 50)
        return False

def main():
    base_url = "http://localhost:8000"
    
    # Test missing filename parameter
    test_endpoint(f"{base_url}/input-file-content", 400)
    
    # Test nonexistent file
    test_endpoint(f"{base_url}/input-file-content?filename=nonexistent.json", 404)
    
    # Test path traversal
    test_endpoint(f"{base_url}/input-file-content?filename=../../../etc/passwd", 403)

if __name__ == '__main__':
    main()
