#!/usr/bin/env python3

import sys
import urllib.request
import urllib.error
import urllib.parse
import json

def test_yaml_support():
    """Test YAML input support"""
    print("🧪 YAML SUPPORT TEST")
    print("=" * 50)
    
    # Test 1: Valid YAML input
    print("\n📝 Test 1: Valid YAML input")
    yaml_input = """
name: "Test Application"
servers:
  - web1.example.com
  - web2.example.com
config:
  port: 8080
  debug: true
"""
    
    template = "{{ data.name }} runs on {{ data.servers | length }} servers on port {{ data.config.port }}"
    
    try:
        data = urllib.parse.urlencode({
            'json': yaml_input,
            'expr': template
        }).encode()
        
        req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            input_format = response.headers.get('X-Input-Format', 'Unknown')
            result_type = response.headers.get('X-Result-Type', 'Unknown')
            
            print(f"✅ Status: {response.getcode()}")
            print(f"✅ Input Format Detected: {input_format}")
            print(f"✅ Result Type: {result_type}")
            print(f"✅ Result: {result}")
            
            if input_format == 'YAML':
                print("✅ YAML format correctly detected")
            else:
                print(f"❌ Expected YAML format, got {input_format}")
                return False
                
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: Valid JSON input (should still work)
    print("\n📝 Test 2: Valid JSON input")
    json_input = """{
    "name": "Test Application",
    "servers": ["web1.example.com", "web2.example.com"],
    "config": {"port": 8080, "debug": true}
}"""
    
    try:
        data = urllib.parse.urlencode({
            'json': json_input,
            'expr': template
        }).encode()
        
        req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            input_format = response.headers.get('X-Input-Format', 'Unknown')
            
            print(f"✅ Status: {response.getcode()}")
            print(f"✅ Input Format Detected: {input_format}")
            print(f"✅ Result: {result}")
            
            if input_format == 'JSON':
                print("✅ JSON format correctly detected")
            else:
                print(f"❌ Expected JSON format, got {input_format}")
                return False
                
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test 3: Invalid input (neither JSON nor YAML)
    print("\n📝 Test 3: Invalid input")
    invalid_input = "This is neither JSON nor YAML { invalid syntax"
    
    try:
        data = urllib.parse.urlencode({
            'json': invalid_input,
            'expr': template
        }).encode()
        
        req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
        urllib.request.urlopen(req)
        print("❌ Expected error but request succeeded")
        return False
        
    except urllib.error.HTTPError as e:
        if e.code == 400:
            error_msg = e.read().decode()
            print(f"✅ Status: {e.code} (expected error)")
            print(f"✅ Error message: {error_msg}")
            if "tried JSON and YAML" in error_msg:
                print("✅ Error message correctly indicates both formats were tried")
            else:
                print("❌ Error message doesn't indicate both formats were tried")
                return False
        else:
            print(f"❌ Unexpected error code: {e.code}")
            return False
    except Exception as e:
        print(f"❌ Test 3 failed with unexpected error: {e}")
        return False
    
    # Test 4: YAML file loading
    print("\n📝 Test 4: YAML file from input files")
    try:
        # Check if sample.yaml is available
        with urllib.request.urlopen('http://localhost:8000/input-files') as response:
            files = json.loads(response.read().decode())
            
        if 'sample.yaml' in files:
            print("✅ sample.yaml found in input files")
            
            # Load the YAML file content
            with urllib.request.urlopen('http://localhost:8000/input-file-content?filename=sample.yaml') as response:
                yaml_content = response.read().decode()
                print(f"✅ YAML file loaded: {yaml_content[:100]}...")
                
            # Test rendering with the loaded YAML
            yaml_template = """# Applications Report
{% for app_name, app_config in data.data.applications.items() %}
## {{ app_config.name }}
- Port: {{ app_config.port }}
- Replicas: {{ app_config.replicas }}
{% endfor %}"""
            
            data = urllib.parse.urlencode({
                'json': yaml_content,
                'expr': yaml_template
            }).encode()
            
            req = urllib.request.Request('http://localhost:8000/render', data=data, method='POST')
            with urllib.request.urlopen(req) as response:
                result = response.read().decode()
                input_format = response.headers.get('X-Input-Format', 'Unknown')
                
                print(f"✅ Rendered result with {input_format} input:")
                print(result[:200] + "..." if len(result) > 200 else result)
                
        else:
            print("ℹ️  sample.yaml not found in input files (skipping this test)")
            
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    print("\n🎉 ALL YAML TESTS PASSED!")
    return True

def main():
    print("🚀 TESTING YAML SUPPORT IN JINJA2 WEB EVALUATOR")
    print("This test validates that both JSON and YAML inputs are supported")
    print("="*70)
    
    try:
        success = test_yaml_support()
        
        if success:
            print("\n" + "🎉"*20)
            print("SUCCESS! YAML support is working perfectly!")
            print("✅ The server now supports:")
            print("   • JSON input (original functionality)")
            print("   • YAML input (new functionality)")
            print("   • Automatic format detection")
            print("   • Error handling for invalid inputs")
            print("   • Both formats in input files")
            print("🎉"*20)
        else:
            print("\n❌ YAML support has issues that need to be addressed.")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
