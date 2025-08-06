import os
import sys
import unittest
import json
import argparse
import tempfile
import shutil
from urllib import request, parse, error

# Configuration: target server
HOST = os.environ.get('TEST_SERVER_HOST', 'localhost')
PORT = int(os.environ.get('TEST_SERVER_PORT', '8000'))
BASE_URL = f'http://{HOST}:{PORT}'

# Default verbosity (override in __main__)
VERBOSITY = 2

class TestJinja2EvalWeb(unittest.TestCase):
    def setUp(self):
        # Reset server state before each test
        # Restore default max_entries
        self.http_request('POST', '/settings', {'section': 'history', 'max_entries': '1000'})
        # Clear history
        self.http_request('POST', '/history/clear')
        
        # Create temporary directory for input files testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = {
            'test1.json': '{"name": "Test User", "age": 25}',
            'test2.json': '{"servers": ["web1", "web2"], "count": 2}',
            'config.json': '{"debug": true, "timeout": 30}'
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)
        
        if VERBOSITY >= 3:
            print(f"Starting test: {self.id()}")
            print(f"Temp directory: {self.temp_dir}")

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Reset input_files configuration
        self.http_request('POST', '/settings', {'section': 'input_files', 'directory': '', 'refresh_interval': '1'})
        
        if VERBOSITY >= 3:
            print('-' * 80)

    def http_request(self, method, path, data=None):
        url = f"{BASE_URL}{path}"
        encoded = parse.urlencode(data).encode() if data else None
        try:
            req = request.Request(url, data=encoded, method=method)
            with request.urlopen(req) as resp:
                content = resp.read().decode()
                ctype = resp.getheader('Content-Type')
                
                # Only try to parse JSON for application/json content type
                if ctype and 'application/json' in ctype:
                    try:
                        parsed = json.loads(content)
                    except json.JSONDecodeError:
                        parsed = content
                else:
                    parsed = content
                    
                if VERBOSITY >= 3:
                    print(f"REQUEST: method={method}, path={path}, data={data}")
                    print(f"RESPONSE: status={resp.status}, content-type={ctype}, body={parsed}")
                return resp.status, ctype, parsed
        except error.HTTPError as e:
            if VERBOSITY >= 3:
                print(f"REQUEST: method={method}, path={path}, data={data}")
                print(f"HTTPError: status={e.code}")
            return e.code, None, None

    def test_root_endpoint(self):
        status, ctype, body = self.http_request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', ctype)
        self.assertTrue(isinstance(body, str) and len(body) > 0)

    def test_render_and_history(self):
        status, _, body = self.http_request('POST', '/render', {'json': '{"a":2}', 'expr': '{{ data.a * 3 }}'})
        self.assertEqual(status, 200)
        self.assertEqual(body, 6)
        _, _, history = self.http_request('GET', '/history')
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 1)
        entry = history[0]
        self.assertEqual(entry['input'], '{"a":2}')
        self.assertEqual(entry['expr'], '{{ data.a * 3 }}')

    def test_history_size_and_maxsize(self):
        # Add entries
        for i in range(2):
            self.http_request('POST', '/render', {'json': f'{{"v":{i}}}', 'expr': '{{ data.v }}'})
        _, _, size_before = self.http_request('GET', '/history/size')
        self.assertEqual(size_before.get('size'), 2)
        _, _, maxsize = self.http_request('GET', '/history/maxsize')
        self.assertIn('max_size', maxsize)
        self.assertIsInstance(maxsize['max_size'], int)

    def test_history_clear(self):
        # Populate history
        for i in range(3):
            self.http_request('POST', '/render', {'json': f'{{"x":{i}}}', 'expr': '{{ data.x }}'})
        _, _, size_before = self.http_request('GET', '/history/size')
        self.assertEqual(size_before.get('size'), 3)
        status, _, clear_resp = self.http_request('POST', '/history/clear', {'count': '2'})
        self.assertEqual(status, 200)
        self.assertEqual(clear_resp.get('cleared'), 2)
        self.assertEqual(clear_resp.get('size'), 1)
        status, _, clear_all = self.http_request('POST', '/history/clear')
        self.assertEqual(status, 200)
        self.assertEqual(clear_all.get('cleared'), 1)
        self.assertEqual(clear_all.get('size'), 0)

    def test_settings_read_and_write(self):
        # Read default settings
        status, _, all_settings = self.http_request('GET', '/settings')
        self.assertEqual(status, 200)
        self.assertIn('history', all_settings)
        self.assertEqual(all_settings['history']['max_entries'], '1000')
        # Update max_entries
        status, _, updated = self.http_request('POST', '/settings', {'section': 'history', 'max_entries': '5'})
        self.assertEqual(status, 200)
        self.assertEqual(updated['history']['max_entries'], '5')
        _, _, maxsize2 = self.http_request('GET', '/history/maxsize')
        self.assertEqual(maxsize2.get('max_size'), 5)
        # Create and read user section
        status, _, user_sec = self.http_request('POST', '/settings', {'section': 'user', 'theme': 'dark'})
        self.assertEqual(status, 200)
        self.assertEqual(user_sec['user']['theme'], 'dark')
        _, _, fetched = self.http_request('GET', '/settings?section=user')
        self.assertEqual(fetched.get('theme'), 'dark')

    def test_404_for_invalid(self):
        status, _, _ = self.http_request('GET', '/invalid_path')
        self.assertEqual(status, 404)

    def test_input_files_endpoint_empty_directory(self):
        """Test input-files endpoint with no directory configured"""
        status, ctype, body = self.http_request('GET', '/input-files')
        self.assertEqual(status, 200)
        self.assertIn('application/json', ctype)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 0)

    def test_input_files_endpoint_with_directory(self):
        """Test input-files endpoint with configured directory"""
        # Configure the input files directory
        self.http_request('POST', '/settings', {
            'section': 'input_files', 
            'directory': self.temp_dir,
            'refresh_interval': '1'
        })
        
        status, ctype, body = self.http_request('GET', '/input-files')
        self.assertEqual(status, 200)
        self.assertIn('application/json', ctype)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 3)
        self.assertIn('test1.json', body)
        self.assertIn('test2.json', body)
        self.assertIn('config.json', body)

    def test_input_file_content_endpoint(self):
        """Test input-file-content endpoint"""
        # Configure the input files directory
        self.http_request('POST', '/settings', {
            'section': 'input_files', 
            'directory': self.temp_dir,
            'refresh_interval': '1'
        })
        
        # Test valid file
        status, ctype, body = self.http_request('GET', '/input-file-content?filename=test1.json')
        self.assertEqual(status, 200)
        self.assertIn('text/plain', ctype)
        self.assertEqual(body, self.test_files['test1.json'])
        
        # Test another valid file
        status, ctype, body = self.http_request('GET', '/input-file-content?filename=test2.json')
        self.assertEqual(status, 200)
        self.assertEqual(body, self.test_files['test2.json'])

    def test_input_file_content_missing_filename(self):
        """Test input-file-content endpoint without filename parameter"""
        status, _, _ = self.http_request('GET', '/input-file-content')
        self.assertEqual(status, 400)

    def test_input_file_content_nonexistent_file(self):
        """Test input-file-content endpoint with non-existent file"""
        # Configure the input files directory
        self.http_request('POST', '/settings', {
            'section': 'input_files', 
            'directory': self.temp_dir,
            'refresh_interval': '1'
        })
        
        status, _, _ = self.http_request('GET', '/input-file-content?filename=nonexistent.json')
        self.assertEqual(status, 404)

    def test_input_file_content_no_directory_configured(self):
        """Test input-file-content endpoint with no directory configured"""
        status, _, _ = self.http_request('GET', '/input-file-content?filename=test1.json')
        self.assertEqual(status, 404)

    def test_input_file_content_security_path_traversal(self):
        """Test input-file-content endpoint security against path traversal"""
        # Configure the input files directory
        self.http_request('POST', '/settings', {
            'section': 'input_files', 
            'directory': self.temp_dir,
            'refresh_interval': '1'
        })
        
        # Try to access file outside the configured directory
        status, _, _ = self.http_request('GET', '/input-file-content?filename=../../../etc/passwd')
        self.assertEqual(status, 403)
        
        # Try another path traversal attempt
        status, _, _ = self.http_request('GET', '/input-file-content?filename=..%2F..%2Fetc%2Fpasswd')
        self.assertEqual(status, 403)

    def test_input_files_settings(self):
        """Test input_files section in settings"""
        # Test setting input_files configuration
        status, _, updated = self.http_request('POST', '/settings', {
            'section': 'input_files',
            'directory': '/tmp/test',
            'refresh_interval': '5'
        })
        self.assertEqual(status, 200)
        self.assertEqual(updated['input_files']['directory'], '/tmp/test')
        self.assertEqual(updated['input_files']['refresh_interval'], '5')
        
        # Test reading input_files configuration
        status, _, config = self.http_request('GET', '/settings?section=input_files')
        self.assertEqual(status, 200)
        self.assertEqual(config.get('directory'), '/tmp/test')
        self.assertEqual(config.get('refresh_interval'), '5')

    def test_input_files_with_relative_path(self):
        """Test input-files endpoint with relative path"""
        # Create a subdirectory for testing relative paths
        rel_dir = 'test_input_files'
        full_rel_dir = os.path.join(os.getcwd(), rel_dir)
        os.makedirs(full_rel_dir, exist_ok=True)
        
        try:
            # Create a test file in the relative directory
            test_file = os.path.join(full_rel_dir, 'relative_test.json')
            with open(test_file, 'w') as f:
                f.write('{"relative": true}')
            
            # Configure with relative path
            self.http_request('POST', '/settings', {
                'section': 'input_files', 
                'directory': rel_dir,
                'refresh_interval': '1'
            })
            
            # Test listing files
            status, _, body = self.http_request('GET', '/input-files')
            self.assertEqual(status, 200)
            self.assertIn('relative_test.json', body)
            
            # Test reading file content
            status, _, content = self.http_request('GET', '/input-file-content?filename=relative_test.json')
            self.assertEqual(status, 200)
            self.assertEqual(content, '{"relative": true}')
            
        finally:
            # Clean up
            shutil.rmtree(full_rel_dir, ignore_errors=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Jinja2 Eval Web tests')
    parser.add_argument('-v', '--verbosity', type=int, default=2,
                        help='Verbosity level for unittest (default: 2)')
    args = parser.parse_args()
    VERBOSITY = args.verbosity
    unittest.main(argv=[sys.argv[0]], verbosity=args.verbosity)
