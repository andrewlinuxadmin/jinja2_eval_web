#!/usr/bin/env python3
"""
Integration test for dynamic file extensions in download functionality.
This test simulates different input formats and verifies the correct behavior.
"""

import urllib.request
import urllib.parse
import json
import time

# Test configuration
SERVER_URL = "http://localhost:8000"

def test_yaml_input_processing():
    """Test that YAML input is properly processed and format detected."""
    print("Testing YAML input processing...")
    
    yaml_data = """
name: "Test User"
age: 30
hobbies:
  - reading
  - programming
  - music
"""
    
    jinja_template = "Hello {{ data.name }}, you are {{ data.age }} years old and enjoy {{ data.hobbies | join(', ') }}!"
    
    try:
        # Prepare the request
        form_data = {
            'json': yaml_data,
            'expr': jinja_template
        }
        
        data = urllib.parse.urlencode(form_data).encode('utf-8')
        req = urllib.request.Request(SERVER_URL + '/render', data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Make the request
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        
        # Check if the input format is correctly detected
        input_format_header = response.headers.get('X-Input-Format')
        
        if input_format_header == 'YAML':
            print("  ✅ YAML format correctly detected")
        else:
            print(f"  ❌ Expected 'YAML' format, got: {input_format_header}")
            return False
        
        # Check if the result is as expected
        expected_result = "Hello Test User, you are 30 years old and enjoy reading, programming, music!"
        if result.strip() == expected_result:
            print("  ✅ YAML data processed correctly")
            return True
        else:
            print(f"  ❌ Expected: {expected_result}")
            print(f"  ❌ Got: {result.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing YAML processing: {e}")
        return False

def test_json_input_processing():
    """Test that JSON input is properly processed and format detected."""
    print("\nTesting JSON input processing...")
    
    json_data = {
        "name": "Test User",
        "age": 25,
        "city": "São Paulo"
    }
    
    jinja_template = "{{ data.name }} lives in {{ data.city }} and is {{ data.age }} years old."
    
    try:
        # Prepare the request
        form_data = {
            'json': json.dumps(json_data, indent=2),
            'expr': jinja_template
        }
        
        data = urllib.parse.urlencode(form_data).encode('utf-8')
        req = urllib.request.Request(SERVER_URL + '/render', data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Make the request
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        
        # Check if the input format is correctly detected
        input_format_header = response.headers.get('X-Input-Format')
        
        if input_format_header == 'JSON':
            print("  ✅ JSON format correctly detected")
        else:
            print(f"  ❌ Expected 'JSON' format, got: {input_format_header}")
            return False
        
        # Check if the result is as expected
        expected_result = "Test User lives in São Paulo and is 25 years old."
        if result.strip() == expected_result:
            print("  ✅ JSON data processed correctly")
            return True
        else:
            print(f"  ❌ Expected: {expected_result}")
            print(f"  ❌ Got: {result.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing JSON processing: {e}")
        return False

def test_input_files_endpoint():
    """Test the input files endpoint for dynamic loading."""
    print("\nTesting input files endpoint...")
    
    try:
        response = urllib.request.urlopen(SERVER_URL + '/input-files')
        files_data = response.read().decode('utf-8')
        files_list = json.loads(files_data)
        
        if isinstance(files_list, list) and len(files_list) > 0:
            print(f"  ✅ Input files endpoint returned {len(files_list)} files")
            
            # Check if we have both JSON and YAML files
            has_json = any(f.endswith('.json') for f in files_list)
            has_yaml = any(f.endswith('.yaml') or f.endswith('.yml') for f in files_list)
            
            if has_json:
                print("  ✅ JSON input files available")
            else:
                print("  ⚠️  No JSON input files found")
            
            if has_yaml:
                print("  ✅ YAML input files available")
            else:
                print("  ⚠️  No YAML input files found")
            
            return True
        else:
            print("  ❌ Input files endpoint returned empty or invalid data")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing input files endpoint: {e}")
        return False

def test_format_detection_consistency():
    """Test that format detection is consistent across different requests."""
    print("\nTesting format detection consistency...")
    
    test_cases = [
        ('{"key": "value"}', 'JSON'),
        ('key: value\nother: data', 'YAML'),
        ('name: "Test"\nage: 30', 'YAML'),
        ('{"name": "Test", "age": 30}', 'JSON')
    ]
    
    all_consistent = True
    
    for test_input, expected_format in test_cases:
        try:
            form_data = {
                'json': test_input,
                'expr': '{{ data.key | default("test") }}'
            }
            
            data = urllib.parse.urlencode(form_data).encode('utf-8')
            req = urllib.request.Request(SERVER_URL + '/render', data=data)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = urllib.request.urlopen(req)
            input_format_header = response.headers.get('X-Input-Format')
            
            if input_format_header == expected_format:
                print(f"  ✅ Format detection consistent for {expected_format}")
            else:
                print(f"  ❌ Expected {expected_format}, got {input_format_header}")
                all_consistent = False
                
        except Exception as e:
            print(f"  ❌ Error testing format detection: {e}")
            all_consistent = False
    
    return all_consistent

def run_all_tests():
    """Run all dynamic extension and format detection tests."""
    print("=" * 60)
    print("DYNAMIC FILE EXTENSION AND FORMAT DETECTION TEST")
    print("=" * 60)
    
    tests = [
        ("YAML Input Processing", test_yaml_input_processing),
        ("JSON Input Processing", test_json_input_processing),
        ("Input Files Endpoint", test_input_files_endpoint),
        ("Format Detection Consistency", test_format_detection_consistency)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Dynamic extensions and format detection are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
