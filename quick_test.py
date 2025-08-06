#!/usr/bin/env python3

import json
import urllib.request
import urllib.parse

def test_endpoint(method, path, data=None):
    url = f"http://localhost:8000{path}"
    encoded = urllib.parse.urlencode(data).encode() if data else None
    try:
        req = urllib.request.Request(url, data=encoded, method=method)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            print(f"✅ {method} {path} - Status: {resp.status}")
            return resp.status
    except Exception as e:
        print(f"❌ {method} {path} - Error: {e}")
        return None

def main():
    print("Testing Jinja2 Eval Web new functionalities...")
    print("=" * 50)
    
    # Test input-files endpoint (should return empty list initially)
    test_endpoint('GET', '/input-files')
    
    # Test input-file-content with missing filename (should return 400)
    test_endpoint('GET', '/input-file-content')
    
    # Test input-file-content with non-existent file (should return 404)
    test_endpoint('GET', '/input-file-content?filename=nonexistent.json')
    
    # Test settings for input_files section
    test_endpoint('POST', '/settings', {
        'section': 'input_files',
        'directory': 'input_examples',
        'refresh_interval': '2'
    })
    
    # Test input-files endpoint after configuration (should return files)
    test_endpoint('GET', '/input-files')
    
    # Test input-file-content with existing file
    test_endpoint('GET', '/input-file-content?filename=person.json')
    
    # Test security - path traversal attempt (should return 403)
    test_endpoint('GET', '/input-file-content?filename=../jinja2_eval_web.py')
    
    print("=" * 50)
    print("All tests completed!")

if __name__ == '__main__':
    main()
