#!/usr/bin/env python3

import sys
import urllib.request
import urllib.error
import json

def test_endpoint(name, url, expected_status, description):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    print(f"Expected Status: {expected_status}")
    print('-' * 60)
    
    try:
        response = urllib.request.urlopen(url)
        status = response.getcode()
        content = response.read().decode()
        content_type = response.headers.get('Content-Type', 'unknown')
        
        print(f"Actual Status: {status}")
        print(f"Content-Type: {content_type}")
        print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        if status == expected_status:
            print("✅ RESULT: PASS")
            return True
        else:
            print(f"❌ RESULT: FAIL - Expected {expected_status}, got {status}")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        if e.code == expected_status:
            print("✅ RESULT: PASS - Expected error received")
            return True
        else:
            print(f"❌ RESULT: FAIL - Expected {expected_status}, got {e.code}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        print("❌ RESULT: FAIL - Unexpected exception")
        return False

def main():
    print("🧪 JINJA2 EVAL WEB - UNIT TESTS")
    print("Testing all server endpoints with detailed descriptions")
    
    tests = [
        ("Root Page", "http://localhost:8000/", 200, 
         "Test if the main HTML page loads correctly"),
        
        ("Input Files - Empty", "http://localhost:8000/input-files", 200, 
         "Test input-files endpoint returns empty array when no directory configured"),
        
        ("Input File Content - Missing Filename", "http://localhost:8000/input-file-content", 400, 
         "Test input-file-content endpoint returns 400 when filename parameter is missing"),
        
        ("Input File Content - No Directory", "http://localhost:8000/input-file-content?filename=test.json", 404, 
         "Test input-file-content returns 404 when no directory is configured"),
        
        ("Settings - All Sections", "http://localhost:8000/settings", 200, 
         "Test settings endpoint returns all configuration sections"),
        
        ("Settings - Input Files Section", "http://localhost:8000/settings?section=input_files", 200, 
         "Test settings endpoint returns input_files section specifically"),
        
        ("History - Size", "http://localhost:8000/history/size", 200, 
         "Test history size endpoint returns current history count"),
        
        ("History - Max Size", "http://localhost:8000/history/maxsize", 200, 
         "Test history maxsize endpoint returns maximum history limit"),
        
        ("History - List", "http://localhost:8000/history", 200, 
         "Test history endpoint returns list of history entries"),
        
        ("Invalid Endpoint", "http://localhost:8000/nonexistent-endpoint", 404, 
         "Test that invalid endpoints return 404 error")
    ]
    
    results = []
    for name, url, expected_status, description in tests:
        result = test_endpoint(name, url, expected_status, description)
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The server is working correctly.")
    else:
        print(f"\n❌ {total - passed} TESTS FAILED. Check the results above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
