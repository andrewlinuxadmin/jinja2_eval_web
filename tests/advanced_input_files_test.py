#!/usr/bin/env python3
"""
Advanced test suite for Jinja2 Eval Web server - Input Files functionality
Tests the new input files features with detailed descriptions
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import tempfile
import os
import shutil

def write_output(message):
    """Write output to both stdout and a file"""
    print(message)
    with open('advanced_test_output.log', 'a') as f:
        f.write(message + '\n')

def make_request(method, path, data=None):
    """Make HTTP request with detailed logging"""
    url = f"http://localhost:8000{path}"
    
    if data:
        encoded_data = urllib.parse.urlencode(data).encode()
    else:
        encoded_data = None
    
    try:
        req = urllib.request.Request(url, data=encoded_data, method=method)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode()
            content_type = response.headers.get('Content-Type', '')
            
            # Parse JSON if appropriate
            if 'application/json' in content_type:
                try:
                    parsed_content = json.loads(content)
                except:
                    parsed_content = content
            else:
                parsed_content = content
            
            return response.getcode(), content_type, parsed_content
            
    except urllib.error.HTTPError as e:
        return e.code, None, str(e.reason)

def test_input_files_functionality():
    """Test the complete input files functionality"""
    write_output("\n" + "="*60)
    write_output("TESTING INPUT FILES FUNCTIONALITY")
    write_output("="*60)
    
    # Test 1: Input files with empty directory configuration
    write_output("\n1. Testing input-files endpoint with empty directory:")
    write_output("   Description: Should return empty array when no directory is configured")
    
    # Reset configuration
    make_request('POST', '/settings', {
        'section': 'input_files',
        'directory': '',
        'refresh_interval': '1'
    })
    
    status, content_type, body = make_request('GET', '/input-files')
    write_output(f"   Request: GET /input-files")
    write_output(f"   Response: {status}, {content_type}, {body}")
    
    test1_pass = status == 200 and isinstance(body, list) and len(body) == 0
    write_output(f"   Result: {'✓ PASS' if test1_pass else '✗ FAIL'}")
    
    # Test 2: Configure directory and test file listing
    write_output("\n2. Testing input files with configured directory:")
    write_output("   Description: Create temp directory with files, configure it, list files")
    
    temp_dir = tempfile.mkdtemp()
    test_files = {
        'example1.json': '{"name": "John", "age": 30}',
        'example2.json': '{"city": "New York", "country": "USA"}',
        'config.json': '{"debug": true, "version": "1.0"}'
    }
    
    try:
        # Create test files
        for filename, content in test_files.items():
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write(content)
        
        write_output(f"   Created temp directory: {temp_dir}")
        write_output(f"   Created files: {list(test_files.keys())}")
        
        # Configure the directory
        status, _, response = make_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        write_output(f"   Configure directory: {status}, {response}")
        
        # List files
        status, content_type, body = make_request('GET', '/input-files')
        write_output(f"   List files: {status}, {body}")
        
        test2_pass = (status == 200 and isinstance(body, list) and 
                     len(body) == 3 and all(f in body for f in test_files.keys()))
        write_output(f"   Result: {'✓ PASS' if test2_pass else '✗ FAIL'}")
        
        # Test 3: Read file content
        write_output("\n3. Testing file content reading:")
        write_output("   Description: Read content of a specific file")
        
        for filename, expected_content in test_files.items():
            status, content_type, body = make_request('GET', f'/input-file-content?filename={filename}')
            write_output(f"   Read {filename}: {status}, {body}")
            
            test3_pass = (status == 200 and 'text/plain' in content_type and body == expected_content)
            write_output(f"   Content matches: {'✓ PASS' if test3_pass else '✗ FAIL'}")
            if not test3_pass:
                write_output(f"   Expected: '{expected_content}'")
                write_output(f"   Got: '{body}'")
        
        # Test 4: Security - Path traversal
        write_output("\n4. Testing security - path traversal protection:")
        write_output("   Description: Attempt path traversal attacks, should be blocked")
        
        dangerous_paths = [
            '../../../etc/passwd',
            '..%2F..%2F..%2Fetc%2Fpasswd',
            '....//....//....//etc/passwd'
        ]
        
        all_blocked = True
        for dangerous_path in dangerous_paths:
            status, _, response = make_request('GET', f'/input-file-content?filename={dangerous_path}')
            write_output(f"   Attempt: {dangerous_path} -> {status}")
            if status != 403:
                all_blocked = False
                write_output(f"   ⚠️  WARNING: Path traversal not blocked! Got {status} instead of 403")
        
        write_output(f"   Security test: {'✓ PASS' if all_blocked else '✗ FAIL'}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        write_output(f"   Cleaned up temp directory")

def test_error_conditions():
    """Test various error conditions"""
    write_output("\n" + "="*60)
    write_output("TESTING ERROR CONDITIONS")
    write_output("="*60)
    
    # Test 1: Missing filename parameter
    write_output("\n1. Testing missing filename parameter:")
    write_output("   Description: Request /input-file-content without filename parameter")
    
    status, _, response = make_request('GET', '/input-file-content')
    write_output(f"   Request: GET /input-file-content")
    write_output(f"   Response: {status} - {response}")
    
    test1_pass = status == 400
    write_output(f"   Result: {'✓ PASS' if test1_pass else '✗ FAIL'} (Expected 400 Bad Request)")
    
    # Test 2: No directory configured
    write_output("\n2. Testing with no directory configured:")
    write_output("   Description: Request file content when no directory is set")
    
    # Ensure no directory is configured
    make_request('POST', '/settings', {
        'section': 'input_files',
        'directory': '',
        'refresh_interval': '1'
    })
    
    status, _, response = make_request('GET', '/input-file-content?filename=test.json')
    write_output(f"   Request: GET /input-file-content?filename=test.json")
    write_output(f"   Response: {status} - {response}")
    
    test2_pass = status == 404
    write_output(f"   Result: {'✓ PASS' if test2_pass else '✗ FAIL'} (Expected 404 Not Found)")
    
    # Test 3: Nonexistent file
    write_output("\n3. Testing nonexistent file:")
    write_output("   Description: Request a file that doesn't exist in configured directory")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Configure directory but don't create the requested file
        make_request('POST', '/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '1'
        })
        
        status, _, response = make_request('GET', '/input-file-content?filename=nonexistent.json')
        write_output(f"   Request: GET /input-file-content?filename=nonexistent.json")
        write_output(f"   Response: {status} - {response}")
        
        test3_pass = status == 404
        write_output(f"   Result: {'✓ PASS' if test3_pass else '✗ FAIL'} (Expected 404 Not Found)")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_settings_functionality():
    """Test settings functionality for input_files"""
    write_output("\n" + "="*60)
    write_output("TESTING SETTINGS FUNCTIONALITY")
    write_output("="*60)
    
    write_output("\n1. Testing input_files settings configuration:")
    write_output("   Description: Set and read input_files configuration")
    
    # Set configuration
    status1, _, response1 = make_request('POST', '/settings', {
        'section': 'input_files',
        'directory': '/tmp/test_directory',
        'refresh_interval': '5'
    })
    write_output(f"   Set config: {status1}, {response1}")
    
    # Read configuration
    status2, _, response2 = make_request('GET', '/settings?section=input_files')
    write_output(f"   Read config: {status2}, {response2}")
    
    test_pass = (
        status1 == 200 and status2 == 200 and
        isinstance(response2, dict) and
        response2.get('directory') == '/tmp/test_directory' and
        response2.get('refresh_interval') == '5'
    )
    write_output(f"   Result: {'✓ PASS' if test_pass else '✗ FAIL'}")

def main():
    """Run all advanced tests"""
    # Clear log file
    with open('advanced_test_output.log', 'w') as f:
        f.write("Jinja2 Eval Web - Advanced Test Results\n")
        f.write("=" * 50 + '\n\n')
    
    write_output("🧪 JINJA2 EVAL WEB - ADVANCED INPUT FILES TESTING")
    write_output("Starting comprehensive tests for input files functionality...")
    
    try:
        test_input_files_functionality()
        test_error_conditions()
        test_settings_functionality()
        
        write_output("\n" + "="*60)
        write_output("🎉 ALL ADVANCED TESTS COMPLETED!")
        write_output("Check advanced_test_output.log for detailed results")
        write_output("="*60)
        
    except Exception as e:
        write_output(f"\n❌ TEST SUITE FAILED WITH EXCEPTION: {e}")
        import traceback
        write_output(traceback.format_exc())

if __name__ == '__main__':
    main()
