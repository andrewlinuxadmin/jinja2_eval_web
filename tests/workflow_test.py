#!/usr/bin/env python3

import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import tempfile
import os
import shutil

def make_post_request(path, data):
    """Make a POST request with form data"""
    url = f"http://localhost:8000{path}"
    encoded_data = urllib.parse.urlencode(data).encode()
    
    try:
        req = urllib.request.Request(url, data=encoded_data, method='POST')
        with urllib.request.urlopen(req) as response:
            content = response.read().decode()
            try:
                return response.getcode(), json.loads(content)
            except:
                return response.getcode(), content
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)

def make_get_request(path):
    """Make a GET request"""
    url = f"http://localhost:8000{path}"
    
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode()
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                try:
                    return response.getcode(), json.loads(content)
                except:
                    return response.getcode(), content
            else:
                return response.getcode(), content
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)

def test_input_files_complete_workflow():
    """Test the complete input files workflow"""
    print("🧪 COMPLETE INPUT FILES WORKFLOW TEST")
    print("=" * 60)
    
    # Step 1: Create temporary directory with test files
    print("\n📁 STEP 1: Creating test files")
    print("Description: Create temporary directory with JSON test files")
    
    temp_dir = tempfile.mkdtemp()
    test_files = {
        'users.json': '{"users": [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]}',
        'config.json': '{"app_name": "MyApp", "version": "1.0", "debug": true}',
        'servers.json': '{"web": ["web1.com", "web2.com"], "db": ["db1.com"]}'
    }
    
    try:
        for filename, content in test_files.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        print(f"✅ Created temp directory: {temp_dir}")
        print(f"✅ Created files: {list(test_files.keys())}")
        
        # Step 2: Configure input files directory
        print("\n⚙️  STEP 2: Configuring input files directory")
        print("Description: Configure server to use our test directory")
        
        status, response = make_post_request('/settings', {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '2'
        })
        
        print(f"POST /settings - Status: {status}")
        print(f"Response: {response}")
        
        if status == 200:
            print("✅ Configuration successful")
        else:
            print("❌ Configuration failed")
            return False
        
        # Step 3: Verify configuration was saved
        print("\n🔍 STEP 3: Verifying configuration")
        print("Description: Read back the configuration to confirm it was saved")
        
        status, config = make_get_request('/settings?section=input_files')
        print(f"GET /settings?section=input_files - Status: {status}")
        print(f"Configuration: {config}")
        
        config_ok = (
            status == 200 and 
            isinstance(config, dict) and
            config.get('directory') == temp_dir and
            config.get('refresh_interval') == '2'
        )
        
        if config_ok:
            print("✅ Configuration verified")
        else:
            print("❌ Configuration verification failed")
            return False
        
        # Step 4: List input files
        print("\n📋 STEP 4: Listing input files")
        print("Description: Get list of available input files from the server")
        
        status, file_list = make_get_request('/input-files')
        print(f"GET /input-files - Status: {status}")
        print(f"Files found: {file_list}")
        
        files_ok = (
            status == 200 and
            isinstance(file_list, list) and
            len(file_list) == 3 and
            all(filename in file_list for filename in test_files.keys())
        )
        
        if files_ok:
            print("✅ File listing successful")
        else:
            print("❌ File listing failed")
            return False
        
        # Step 5: Read file contents
        print("\n📖 STEP 5: Reading file contents")
        print("Description: Read content of each test file")
        
        all_content_ok = True
        for filename, expected_content in test_files.items():
            status, content = make_get_request(f'/input-file-content?filename={filename}')
            print(f"GET /input-file-content?filename={filename} - Status: {status}")
            print(f"Content: {content}")
            
            if status == 200 and content == expected_content:
                print(f"✅ {filename} content correct")
            else:
                print(f"❌ {filename} content incorrect")
                print(f"   Expected: {expected_content}")
                print(f"   Got: {content}")
                all_content_ok = False
        
        if not all_content_ok:
            return False
        
        # Step 6: Test error conditions
        print("\n🚫 STEP 6: Testing error conditions")
        print("Description: Test various error scenarios")
        
        # Test nonexistent file
        status, response = make_get_request('/input-file-content?filename=nonexistent.json')
        print(f"Nonexistent file test - Status: {status} (expected 404)")
        
        if status != 404:
            print("❌ Nonexistent file should return 404")
            return False
        
        # Test path traversal
        status, response = make_get_request('/input-file-content?filename=../../../etc/passwd')
        print(f"Path traversal test - Status: {status} (expected 403)")
        
        if status != 403:
            print("❌ Path traversal should return 403")
            return False
        
        print("✅ Error conditions handled correctly")
        
        # Step 7: Test with render endpoint
        print("\n🎨 STEP 7: Testing integration with render endpoint")
        print("Description: Use file content with Jinja2 rendering")
        
        # Get users.json content and use it in a template
        status, users_content = make_get_request('/input-file-content?filename=users.json')
        
        if status == 200:
            # Use the content in a render request
            render_status, render_response = make_post_request('/render', {
                'json': users_content,
                'expr': '{% for user in data.users %}{{ user.name }}: {{ user.role }}\n{% endfor %}'
            })
            
            print(f"Render with file content - Status: {render_status}")
            print(f"Rendered output: {render_response}")
            
            expected_output = "Alice: admin\nBob: user\n"
            if render_status == 200 and render_response == expected_output:
                print("✅ Integration with render endpoint successful")
            else:
                print("❌ Integration with render endpoint failed")
                return False
        
        print("\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
        print("✅ Complete input files workflow is working correctly")
        return True
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Reset configuration
        make_post_request('/settings', {
            'section': 'input_files',
            'directory': '',
            'refresh_interval': '1'
        })
        print("✅ Configuration reset")

def main():
    """Run the complete workflow test"""
    print("🚀 STARTING COMPREHENSIVE INPUT FILES TEST")
    print("This test will verify the complete input files functionality")
    
    try:
        success = test_input_files_complete_workflow()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ALL TESTS PASSED! Input files functionality is working perfectly.")
            print("✅ The server correctly handles:")
            print("   - Directory configuration")
            print("   - File listing")
            print("   - File content reading")
            print("   - Error handling")
            print("   - Security (path traversal protection)")
            print("   - Integration with rendering")
        else:
            print("❌ SOME TESTS FAILED! Check the output above for details.")
        
        return success
        
    except Exception as e:
        print(f"\n💥 TEST SUITE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
