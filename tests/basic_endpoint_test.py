#!/usr/bin/env python3

import urllib.request
import urllib.error
import json
import sys

def write_output(message):
    """Write output to both stdout and a file"""
    print(message)
    with open('test_output.log', 'a') as f:
        f.write(message + '\n')

def test_endpoint(name, url, expect_status=200, expect_error=False):
    """Test a single endpoint"""
    write_output(f"\n--- Testing {name} ---")
    write_output(f"URL: {url}")
    
    try:
        response = urllib.request.urlopen(url)
        status = response.getcode()
        content = response.read().decode()
        content_type = response.headers.get('Content-Type', '')
        
        write_output(f"Status: {status}")
        write_output(f"Content-Type: {content_type}")
        write_output(f"Content (first 100 chars): {content[:100]}")
        
        if status == expect_status:
            write_output("✓ PASS")
            return True
        else:
            write_output(f"✗ FAIL - Expected {expect_status}, got {status}")
            return False
            
    except urllib.error.HTTPError as e:
        write_output(f"HTTP Error: {e.code} - {e.reason}")
        if expect_error and e.code == expect_status:
            write_output("✓ PASS - Expected error received")
            return True
        else:
            write_output(f"✗ FAIL - Unexpected error or wrong status")
            return False
    except Exception as e:
        write_output(f"Exception: {e}")
        write_output("✗ FAIL - Exception occurred")
        return False

def main():
    # Clear log file
    with open('test_output.log', 'w') as f:
        f.write("Jinja2 Eval Web Test Results\n")
        f.write("=" * 40 + '\n')
    
    write_output("Starting Jinja2 Eval Web endpoint tests...")
    
    tests = [
        ("Root endpoint", "http://localhost:8000/", 200, False),
        ("Input files endpoint", "http://localhost:8000/input-files", 200, False),
        ("Input file content - missing filename", "http://localhost:8000/input-file-content", 400, True),
        ("Input file content - nonexistent file", "http://localhost:8000/input-file-content?filename=nonexistent.json", 404, True),
        ("Settings endpoint", "http://localhost:8000/settings", 200, False),
        ("History size", "http://localhost:8000/history/size", 200, False),
        ("Invalid endpoint", "http://localhost:8000/invalid", 404, True)
    ]
    
    results = []
    for name, url, expect_status, expect_error in tests:
        result = test_endpoint(name, url, expect_status, expect_error)
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    write_output(f"\n=== SUMMARY ===")
    write_output(f"Tests run: {total}")
    write_output(f"Passed: {passed}")
    write_output(f"Failed: {total - passed}")
    
    if passed == total:
        write_output("🎉 ALL TESTS PASSED!")
    else:
        write_output("❌ SOME TESTS FAILED")
    
    write_output("\nDetailed results saved to test_output.log")

if __name__ == '__main__':
    main()
