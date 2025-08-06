#!/usr/bin/env python3
"""
Test for download button layout and dynamic file extensions.
"""

import urllib.request
import urllib.parse
import json
import re
import time

# Test configuration
SERVER_URL = "http://localhost:8000"

def test_html_layout():
    """Test if download buttons are properly aligned in the HTML structure."""
    print("Testing HTML layout for download buttons...")
    
    try:
        # Get the main page
        response = urllib.request.urlopen(SERVER_URL)
        html_content = response.read().decode('utf-8')
        
        # Check for proper button structure
        button_patterns = [
            r'<button class="btn btn-sm btn-outline-secondary" onclick="downloadInputContent\(\)">',
            r'<button class="btn btn-sm btn-outline-secondary" onclick="downloadExpressionContent\(\)">',
            r'<button class="btn btn-sm btn-outline-secondary" onclick="downloadResultContent\(\)">'
        ]
        
        all_buttons_found = True
        for pattern in button_patterns:
            if not re.search(pattern, html_content):
                print(f"  ❌ Button pattern not found: {pattern}")
                all_buttons_found = False
            else:
                print(f"  ✅ Button pattern found: {pattern}")
        
        # Check for proper flexbox layout
        flex_patterns = [
            r'<div class="d-flex justify-content-between align-items-center mb-2">',
        ]
        
        for pattern in flex_patterns:
            matches = re.findall(pattern, html_content)
            if len(matches) >= 3:  # Should have 3 cards with this layout
                print(f"  ✅ Flexbox layout found {len(matches)} times")
            else:
                print(f"  ❌ Flexbox layout found only {len(matches)} times, expected 3")
                all_buttons_found = False
        
        # Check for download functions
        function_patterns = [
            r'function downloadInputContent\(\)',
            r'function downloadExpressionContent\(\)',
            r'function downloadResultContent\(\)',
            r'function getExtensionFromMode\(mode\)'
        ]
        
        for pattern in function_patterns:
            if re.search(pattern, html_content):
                print(f"  ✅ Function found: {pattern}")
            else:
                print(f"  ❌ Function not found: {pattern}")
                all_buttons_found = False
        
        return all_buttons_found
        
    except Exception as e:
        print(f"  ❌ Error testing HTML layout: {e}")
        return False

def test_extension_mapping():
    """Test the extension mapping logic in JavaScript."""
    print("\nTesting extension mapping logic...")
    
    try:
        # Get the main page to check JavaScript logic
        response = urllib.request.urlopen(SERVER_URL)
        html_content = response.read().decode('utf-8')
        
        # Check for extension mapping
        extension_mapping = re.search(
            r'const extensions = \{([^}]+)\}', 
            html_content, 
            re.DOTALL
        )
        
        if extension_mapping:
            print("  ✅ Extension mapping found in JavaScript")
            mapping_content = extension_mapping.group(1)
            
            # Check for expected mappings
            expected_mappings = [
                "'application/json': 'json'",
                "'text/x-yaml': 'yaml'",
                "'application/xml': 'xml'",
                "'text/plain': 'txt'",
                "'jinja2': 'j2'"
            ]
            
            all_mappings_found = True
            for mapping in expected_mappings:
                if mapping in mapping_content:
                    print(f"    ✅ Mapping found: {mapping}")
                else:
                    print(f"    ❌ Mapping not found: {mapping}")
                    all_mappings_found = False
            
            return all_mappings_found
        else:
            print("  ❌ Extension mapping not found in JavaScript")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing extension mapping: {e}")
        return False

def test_button_positioning():
    """Test if buttons are no longer using absolute positioning."""
    print("\nTesting button positioning (should not use absolute positioning)...")
    
    try:
        response = urllib.request.urlopen(SERVER_URL)
        html_content = response.read().decode('utf-8')
        
        # Check that old absolute positioning is removed
        old_patterns = [
            r'position-absolute',
            r'style="top:10px; right:10px; z-index:10;"'
        ]
        
        no_old_positioning = True
        for pattern in old_patterns:
            if re.search(pattern, html_content):
                print(f"  ❌ Old positioning pattern still found: {pattern}")
                no_old_positioning = False
            else:
                print(f"  ✅ Old positioning pattern removed: {pattern}")
        
        return no_old_positioning
        
    except Exception as e:
        print(f"  ❌ Error testing button positioning: {e}")
        return False

def run_all_tests():
    """Run all layout and functionality tests."""
    print("=" * 60)
    print("BUTTON LAYOUT AND DOWNLOAD FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        ("HTML Layout", test_html_layout),
        ("Extension Mapping", test_extension_mapping),
        ("Button Positioning", test_button_positioning)
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
        print("🎉 All tests passed! Button layout and download functionality are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
