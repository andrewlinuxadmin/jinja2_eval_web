#!/usr/bin/env python3

import urllib.request
import json

def test_server():
    try:
        # Test basic connection
        print("Testing server connection...")
        response = urllib.request.urlopen("http://localhost:8000/")
        status = response.getcode()
        print(f"Server status: {status}")
        
        # Test input-files endpoint
        print("\nTesting /input-files endpoint...")
        response = urllib.request.urlopen("http://localhost:8000/input-files")
        content = response.read().decode()
        print(f"Response: {content}")
        
        # Test input-file-content without filename
        print("\nTesting /input-file-content without filename...")
        try:
            response = urllib.request.urlopen("http://localhost:8000/input-file-content")
            print(f"Unexpected success: {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"Expected error: {e.code} - {e.reason}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_server()
