#!/usr/bin/env python3
"""
Comprehensive test suite for Jinja2 Eval Web server endpoints.
This script tests all server endpoints with clear descriptions.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import os
import shutil

# Server configuration
BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test_header(test_name, description):
    """Print a formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.END}")
    print(f"{Colors.YELLOW}Description: {description}{Colors.END}")
    print("-" * 60)

def print_result(success, message=""):
    """Print test result with color coding"""
    if success:
        print(f"{Colors.GREEN}✓ PASS{Colors.END} {message}")
    else:
        print(f"{Colors.RED}✗ FAIL{Colors.END} {message}")
    print()

def http_request(method, path, data=None, expect_error=False):
    """Make HTTP request to server"""
    url = f"{BASE_URL}{path}"
    encoded = urllib.parse.urlencode(data).encode() if data else None
    
    try:
        req = urllib.request.Request(url, data=encoded, method=method)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            content_type = resp.getheader('Content-Type', '')
            
            # Parse JSON if content type indicates it
            if 'application/json' in content_type:
                try:
                    parsed_content = json.loads(content)
                except json.JSONDecodeError:
                    parsed_content = content
            else:
                parsed_content = content
            
            print(f"Request: {method} {path}")
            if data:
                print(f"Data: {data}")
            print(f"Response Status: {resp.status}")
            print(f"Content-Type: {content_type}")
            print(f"Content: {str(parsed_content)[:200]}{'...' if len(str(parsed_content)) > 200 else ''}")
            
            return resp.status, content_type, parsed_content
            
    except urllib.error.HTTPError as e:
        print(f"Request: {method} {path}")
        if data:
            print(f"Data: {data}")
        print(f"HTTP Error Status: {e.code}")
        print(f"Error Reason: {e.reason}")
        
        if expect_error:
            return e.code, None, None
        else:
            return e.code, None, f"Unexpected error: {e.reason}"

def reset_server_state():
    """Reset server to known state"""
    # Clear history
    http_request('POST', '/history/clear')
    # Reset input_files configuration
    http_request('POST', '/settings', {
        'section': 'input_files', 
        'directory': '', 
        'refresh_interval': '1'
    })

def test_root_endpoint():
    """Test the root endpoint returns HTML page"""
    print_test_header(
        "Root Endpoint", 
        "Testing GET / - should return HTML page with status 200"
    )
    
    status, content_type, body = http_request('GET', '/')
    
    success = (
        status == 200 and 
        content_type and 'text/html' in content_type and
        isinstance(body, str) and len(body) > 0 and
        'Jinja2' in body
    )
    
    print_result(success, f"Expected: 200 HTML page, Got: {status} {content_type}")
    return success

def test_input_files_empty():
    """Test input-files endpoint with no directory configured"""
    print_test_header(
        "Input Files - Empty Directory",
        "Testing GET /input-files with no directory configured - should return empty JSON array"
    )
    
    # Ensure no directory is configured
    reset_server_state()
    
    status, content_type, body = http_request('GET', '/input-files')
    
    success = (
        status == 200 and
        'application/json' in content_type and
        isinstance(body, list) and
        len(body) == 0
    )
    
    print_result(success, f"Expected: 200 empty array, Got: {status} {body}")
    return success

def test_input_files_with_directory():
    """Test input-files endpoint with configured directory"""
    print_test_header(
        "Input Files - With Directory",
        "Testing GET /input-files with configured directory containing test files"
    )
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    test_files = ['test1.json', 'test2.json', 'config.json']
    
    try:
        for filename in test_files:
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write('{"test": true}')
        
        # Configure directory
        http_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        
        status, content_type, body = http_request('GET', '/input-files')
        
        success = (
            status == 200 and
            'application/json' in content_type and
            isinstance(body, list) and
            len(body) == 3 and
            all(filename in body for filename in test_files)
        )
        
        print_result(success, f"Expected: 200 with 3 files, Got: {status} {body}")
        return success
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_input_file_content_missing_filename():
    """Test input-file-content endpoint without filename parameter"""
    print_test_header(
        "Input File Content - Missing Filename",
        "Testing GET /input-file-content without filename parameter - should return 400"
    )
    
    status, content_type, body = http_request('GET', '/input-file-content', expect_error=True)
    
    success = status == 400
    print_result(success, f"Expected: 400 Bad Request, Got: {status}")
    return success

def test_input_file_content_no_directory():
    """Test input-file-content endpoint with no directory configured"""
    print_test_header(
        "Input File Content - No Directory",
        "Testing GET /input-file-content with filename but no directory configured - should return 404"
    )
    
    # Ensure no directory is configured
    reset_server_state()
    
    status, content_type, body = http_request('GET', '/input-file-content?filename=test.json', expect_error=True)
    
    success = status == 404
    print_result(success, f"Expected: 404 Not Found, Got: {status}")
    return success

def test_input_file_content_nonexistent_file():
    """Test input-file-content endpoint with non-existent file"""
    print_test_header(
        "Input File Content - Nonexistent File",
        "Testing GET /input-file-content with valid directory but non-existent file - should return 404"
    )
    
    # Create temporary directory (but no files)
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configure directory
        http_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        
        status, content_type, body = http_request('GET', '/input-file-content?filename=nonexistent.json', expect_error=True)
        
        success = status == 404
        print_result(success, f"Expected: 404 Not Found, Got: {status}")
        return success
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_input_file_content_valid_file():
    """Test input-file-content endpoint with valid file"""
    print_test_header(
        "Input File Content - Valid File",
        "Testing GET /input-file-content with valid file - should return 200 with file content"
    )
    
    # Create temporary directory with test file
    temp_dir = tempfile.mkdtemp()
    test_content = '{"name": "Test User", "age": 25}'
    
    try:
        with open(os.path.join(temp_dir, 'test.json'), 'w') as f:
            f.write(test_content)
        
        # Configure directory
        http_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        
        status, content_type, body = http_request('GET', '/input-file-content?filename=test.json')
        
        success = (
            status == 200 and
            'text/plain' in content_type and
            body == test_content
        )
        
        print_result(success, f"Expected: 200 with content '{test_content}', Got: {status} '{body}'")
        return success
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_input_file_content_path_traversal():
    """Test input-file-content endpoint security against path traversal"""
    print_test_header(
        "Input File Content - Path Traversal Security",
        "Testing GET /input-file-content with path traversal attempts - should return 403"
    )
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configure directory
        http_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        
        # Test path traversal attempts
        traversal_attempts = [
            '../../../etc/passwd',
            '..%2F..%2F..%2Fetc%2Fpasswd',
            '....//....//....//etc/passwd'
        ]
        
        all_blocked = True
        for attempt in traversal_attempts:
            status, _, _ = http_request('GET', f'/input-file-content?filename={attempt}', expect_error=True)
            if status != 403:
                all_blocked = False
                print(f"Path traversal attempt '{attempt}' returned {status} instead of 403")
        
        print_result(all_blocked, f"All path traversal attempts should return 403")
        return all_blocked
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_settings_input_files():
    """Test input_files settings configuration"""
    print_test_header(
        "Settings - Input Files Configuration",
        "Testing POST /settings for input_files section and GET /settings to read it back"
    )
    
    # Test setting configuration
    status1, _, response1 = http_request('POST', '/settings', {
        'section': 'input_files',
        'directory': '/tmp/test',
        'refresh_interval': '5'
    })
    
    # Test reading configuration
    status2, _, response2 = http_request('GET', '/settings?section=input_files')
    
    success = (
        status1 == 200 and
        status2 == 200 and
        isinstance(response1, dict) and
        isinstance(response2, dict) and
        response2.get('directory') == '/tmp/test' and
        response2.get('refresh_interval') == '5'
    )
    
    print_result(success, f"Setting: {status1}, Reading: {status2}, Values: {response2}")
    return success

def test_render_endpoint():
    """Test the render endpoint with valid Jinja2 template"""
    print_test_header(
        "Render Endpoint",
        "Testing POST /render with valid JSON and Jinja2 template - should return rendered result"
    )
    
    status, content_type, body = http_request('POST', '/render', {
        'json': '{"name": "World"}',
        'expr': 'Hello {{ data.name }}!'
    })
    
    success = (
        status == 200 and
        body == 'Hello World!'
    )
    
    print_result(success, f"Expected: 200 'Hello World!', Got: {status} '{body}'")
    return success

def test_history_endpoints():
    """Test history-related endpoints"""
    print_test_header(
        "History Endpoints",
        "Testing history functionality: render to create history, get history size, clear history"
    )
    
    # Clear history first
    http_request('POST', '/history/clear')
    
    # Create some history entries
    http_request('POST', '/render', {'json': '{"test": 1}', 'expr': '{{ data.test }}'})
    http_request('POST', '/render', {'json': '{"test": 2}', 'expr': '{{ data.test }}'})
    
    # Check history size
    status1, _, size_response = http_request('GET', '/history/size')
    
    # Get history
    status2, _, history = http_request('GET', '/history')
    
    # Clear history
    status3, _, clear_response = http_request('POST', '/history/clear')
    
    # Check size after clear
    status4, _, final_size = http_request('GET', '/history/size')
    
    success = (
        status1 == 200 and size_response.get('size') == 2 and
        status2 == 200 and isinstance(history, list) and len(history) == 2 and
        status3 == 200 and clear_response.get('cleared') == 2 and
        status4 == 200 and final_size.get('size') == 0
    )
    
    print_result(success, f"History operations: Size={size_response}, Clear={clear_response}, Final={final_size}")
    return success

def test_404_endpoint():
    """Test invalid endpoint returns 404"""
    print_test_header(
        "404 Error Handling",
        "Testing GET /invalid-endpoint - should return 404"
    )
    
    status, _, _ = http_request('GET', '/invalid-endpoint', expect_error=True)
    
    success = status == 404
    print_result(success, f"Expected: 404 Not Found, Got: {status}")
    return success

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}Jinja2 Eval Web - Comprehensive Endpoint Test Suite{Colors.END}")
    print("=" * 60)
    
    # List of all test functions
    tests = [
        test_root_endpoint,
        test_input_files_empty,
        test_input_files_with_directory,
        test_input_file_content_missing_filename,
        test_input_file_content_no_directory,
        test_input_file_content_nonexistent_file,
        test_input_file_content_valid_file,
        test_input_file_content_path_traversal,
        test_settings_input_files,
        test_render_endpoint,
        test_history_endpoints,
        test_404_endpoint
    ]
    
    # Run all tests
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"{Colors.RED}ERROR: Test {test_func.__name__} failed with exception: {e}{Colors.END}")
            results.append(False)
        
        # Reset server state between tests
        reset_server_state()
    
    # Print summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {total - passed}{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.END}")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
