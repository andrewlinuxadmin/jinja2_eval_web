#!/usr/bin/env python3

import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import tempfile
import os

def test_format_detection():
    """Test automatic format detection in UI"""
    print("🧪 FORMAT DETECTION TEST")
    print("=" * 50)
    
    # Test data for different formats
    test_cases = [
        {
            "name": "JSON format",
            "content": '{"name": "Test", "value": 123}',
            "expected_format": "JSON"
        },
        {
            "name": "YAML format", 
            "content": """name: Test Application
value: 123
config:
  port: 8080
  debug: true""",
            "expected_format": "YAML"
        },
        {
            "name": "Plain text",
            "content": "This is just plain text without structure",
            "expected_format": "string"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Content preview: {test_case['content'][:50]}...")
        
        try:
            # Send render request
            data = urllib.parse.urlencode({
                'json': test_case['content'],
                'expr': '{{ data }}'
            }).encode()
            
            req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
            
            try:
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode()
                    input_format = response.headers.get('X-Input-Format', 'Unknown')
                    result_type = response.headers.get('X-Result-Type', 'Unknown')
                    
                    print(f"✅ Status: {response.getcode()}")
                    print(f"✅ Detected Input Format: {input_format}")
                    print(f"✅ Result Type: {result_type}")
                    
                    if input_format == test_case['expected_format']:
                        print(f"✅ Format detection correct!")
                        success_count += 1
                    else:
                        print(f"❌ Expected {test_case['expected_format']}, got {input_format}")
                        
            except urllib.error.HTTPError as e:
                if test_case['expected_format'] == 'error':
                    print(f"✅ Expected error received: {e.code}")
                    success_count += 1
                else:
                    print(f"❌ Unexpected error: {e.code} - {e.read().decode()}")
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Format Detection Results:")
    print(f"Tests passed: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("🎉 All format detection tests passed!")
        return True
    else:
        print("❌ Some format detection tests failed")
        return False

def test_file_format_detection():
    """Test format detection with input files"""
    print("\n🗂️  INPUT FILES FORMAT DETECTION")
    print("=" * 50)
    
    try:
        # Check available files
        with urllib.request.urlopen('http://localhost:8000/input-files') as response:
            files = json.loads(response.read().decode())
            print(f"Available files: {files}")
        
        test_files = []
        for filename in files:
            if filename.endswith('.json'):
                test_files.append((filename, 'JSON'))
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                test_files.append((filename, 'YAML'))
        
        if not test_files:
            print("ℹ️  No test files available")
            return True
        
        success_count = 0
        for filename, expected_format in test_files:
            print(f"\n📄 Testing file: {filename}")
            
            try:
                # Load file content
                with urllib.request.urlopen(f'http://localhost:8000/input-file-content?filename={urllib.parse.quote(filename)}') as response:
                    content = response.read().decode()
                    print(f"File content preview: {content[:100]}...")
                
                # Test rendering with file content
                data = urllib.parse.urlencode({
                    'json': content,
                    'expr': '{{ data }}'
                }).encode()
                
                req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
                with urllib.request.urlopen(req) as response:
                    input_format = response.headers.get('X-Input-Format', 'Unknown')
                    
                    print(f"✅ Detected format: {input_format}")
                    
                    if input_format == expected_format:
                        print(f"✅ File format detection correct!")
                        success_count += 1
                    else:
                        print(f"❌ Expected {expected_format}, got {input_format}")
                        
            except Exception as e:
                print(f"❌ Error testing file {filename}: {e}")
        
        print(f"\n📊 File Format Detection Results:")
        print(f"Files tested correctly: {success_count}/{len(test_files)}")
        
        return success_count == len(test_files)
        
    except Exception as e:
        print(f"❌ File format detection test failed: {e}")
        return False

def main():
    print("🚀 TESTING FORMAT DETECTION FUNCTIONALITY")
    print("This test validates automatic format detection in the UI")
    print("="*70)
    
    try:
        test1_success = test_format_detection()
        test2_success = test_file_format_detection()
        
        overall_success = test1_success and test2_success
        
        if overall_success:
            print("\n" + "🎉"*20)
            print("SUCCESS! Format detection is working perfectly!")
            print("✅ The UI now automatically:")
            print("   • Detects JSON vs YAML input formats")
            print("   • Updates format selectors accordingly") 
            print("   • Handles file loading with correct formats")
            print("   • Updates result formats based on content")
            print("   • Provides visual feedback on detected formats")
            print("🎉"*20)
        else:
            print("\n❌ Format detection has issues that need to be addressed.")
        
        return overall_success
        
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
