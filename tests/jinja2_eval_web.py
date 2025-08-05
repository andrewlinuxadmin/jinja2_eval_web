import json
import sys
import os
import time
import threading
import signal
import configparser
import datetime
import base64

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from jinja2.sandbox import SandboxedEnvironment as Environment
from jinja2 import StrictUndefined
from ansible.plugins.filter.core import FilterModule as CoreFilters
from ansible.plugins.filter.mathstuff import FilterModule as MathFilters
from ansible.plugins.filter.urls import FilterModule as UrlFilters

HOST = 'localhost'
PORT = 8000

CURRENT_DIR = os.path.dirname(__file__)
SCRIPT_BASE = os.path.splitext(os.path.basename(__file__))[0]
HTML_FILE_PATH = os.path.join(CURRENT_DIR, SCRIPT_BASE + '.html')
CONF_PATH = os.path.join(CURRENT_DIR, SCRIPT_BASE + '.conf')
JSON_HISTORY_PATH = os.path.join(CURRENT_DIR, SCRIPT_BASE + '.json')

# Load or create configuration
config = configparser.ConfigParser()
if not os.path.exists(CONF_PATH):
  config['history'] = {'max_entries': '1000'}
  with open(CONF_PATH, 'w', encoding='utf-8') as conf_file:
    config.write(conf_file)
else:
  config.read(CONF_PATH)

# Initial max entries
MAX_ENTRIES = int(config.get('history', 'max_entries', fallback='1000'))

with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
  HTML_PAGE = f.read()

env = Environment(
  trim_blocks=True,
  lstrip_blocks=True,
  undefined=StrictUndefined
)
env.filters.update(CoreFilters().filters())
env.filters.update(MathFilters().filters())
env.filters.update(UrlFilters().filters())

class JinjaHandler(BaseHTTPRequestHandler):
  def _send_headers(self, status=200, content_type='text/html', extra_headers=None):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    self.send_header('Pragma', 'no-cache')
    self.send_header('Expires', '0')
    if extra_headers:
      for key, value in extra_headers.items():
        self.send_header(key, value)
    self.end_headers()

  def do_GET(self):
    parsed = urlparse(self.path)
    path = parsed.path
    params = parse_qs(parsed.query)

    if path == '/history':
      self._send_headers(200, 'application/json')
      try:
        with open(JSON_HISTORY_PATH, 'r', encoding='utf-8') as hist_file:
          raw_history = json.load(hist_file)
      except Exception:
        raw_history = []
      decoded = []
      for entry in raw_history:
        e = entry.copy()
        try:
          e['input'] = base64.b64decode(e.get('input', '')).decode('utf-8')
        except Exception:
          pass
        try:
          e['expr'] = base64.b64decode(e.get('expr', '')).decode('utf-8')
        except Exception:
          pass
        decoded.append(e)
      self.wfile.write(json.dumps(decoded, indent=2).encode('utf-8'))
      return

    if path == '/history/size':
      self._send_headers(200, 'application/json')
      try:
        with open(JSON_HISTORY_PATH, 'r', encoding='utf-8') as f:
          hist = json.load(f)
      except Exception:
        hist = []
      self.wfile.write(json.dumps({'size': len(hist)}).encode('utf-8'))
      return

    if path == '/history/maxsize':
      self._send_headers(200, 'application/json')
      self.wfile.write(json.dumps({'max_size': MAX_ENTRIES}).encode('utf-8'))
      return

    if path == '/settings':
      self._send_headers(200, 'application/json')
      section = params.get('section', [None])[0]
      if section:
        data = dict(config[section]) if config.has_section(section) else {}
      else:
        data = {s: dict(config[s]) for s in config.sections()}
      self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
      return

    if path != '/':
      self.send_error(404, 'File not found')
      return

    self._send_headers()
    self.wfile.write(HTML_PAGE.encode('utf-8'))

  def do_POST(self):
    global MAX_ENTRIES
    parsed = urlparse(self.path)
    path = parsed.path
    length = int(self.headers.get('Content-Length', 0))
    post_data = self.rfile.read(length)
    params = parse_qs(post_data.decode())

    if path == '/history/clear':
      count = params.get('count', [None])[0]
      try:
        with open(JSON_HISTORY_PATH, 'r', encoding='utf-8') as f:
          hist = json.load(f)
      except Exception:
        hist = []
      original = len(hist)
      if count is None:
        hist = []
        cleared = original
      else:
        try:
          n = int(count)
          cleared = min(n, original)
          hist = hist[cleared:]
        except Exception:
          hist = []
          cleared = original
      with open(JSON_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(hist, f, indent=2)
      self._send_headers(200, 'application/json')
      self.wfile.write(json.dumps({'cleared': cleared, 'size': len(hist)}).encode('utf-8'))
      return

    if path == '/settings':
      section = params.get('section', [None])[0]
      if not section:
        self._send_headers(400, 'application/json')
        self.wfile.write(json.dumps({'error': 'Missing section parameter'}).encode('utf-8'))
        return
      if not config.has_section(section):
        config[section] = {}
      for k, v in params.items():
        if k == 'section':
          continue
        config[section][k] = v[0]
      with open(CONF_PATH, 'w', encoding='utf-8') as cf:
        config.write(cf)
      # update max entries if history section changed
      if section == 'history' and 'max_entries' in config['history']:
        try:
          MAX_ENTRIES = int(config.get('history', 'max_entries'))
        except Exception:
          pass
      self._send_headers(200, 'application/json')
      self.wfile.write(json.dumps({section: dict(config[section])}, indent=2).encode('utf-8'))
      return

    if path != '/render':
      self._send_headers(404)
      self.send_error(404, 'Endpoint not found')
      return

    json_text = params.get('json', [''])[0]
    expr = params.get('expr', [''])[0]

    try:
      data = json.loads(json_text)
    except Exception as e:
      self._send_headers(400, 'text/plain')
      self.wfile.write(f'JSON parsing error: {e}'.encode())
      return

    try:
      template = env.from_string(expr)
      output = template.render(data=data)
      try:
        parsed_out = json.loads(output)
        output = json.dumps(parsed_out, indent=2)
        headers = {'X-Result-Type': 'json'}
      except Exception:
        headers = {'X-Result-Type': 'string'}

      # Record
      try:
        ts = datetime.datetime.utcnow().isoformat() + 'Z'
        entry = {
          'datetime': ts,
          'input': base64.b64encode(json_text.encode('utf-8')).decode('ascii'),
          'expr': base64.b64encode(expr.encode('utf-8')).decode('ascii')
        }
        try:
          with open(JSON_HISTORY_PATH, 'r', encoding='utf-8') as hf:
            hist = json.load(hf)
        except Exception:
          hist = []
        hist.append(entry)
        hist = hist[-MAX_ENTRIES:]
        with open(JSON_HISTORY_PATH, 'w', encoding='utf-8') as hf:
          json.dump(hist, hf, indent=2)
      except Exception:
        pass

      self._send_headers(200, 'text/plain', headers)
      self.wfile.write(output.encode())
    except Exception as e:
      self._send_headers(400, 'text/plain')
      self.wfile.write(f'Jinja expression error: {e}'.encode())

if __name__ == '__main__':
  def watch_files(paths):
    last_mtimes = {p: os.path.getmtime(p) for p in paths}
    while True:
      time.sleep(1)
      for p, m in last_mtimes.items():
        try:
          if os.path.getmtime(p) != m:
            print(f'Reloading due to change in {os.path.basename(p)}...')
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
          continue

  files = [__file__, HTML_FILE_PATH, CONF_PATH]
  threading.Thread(target=watch_files, args=(files,), daemon=True).start()
  print(f"Server started at http://{HOST}:{PORT}")
  HTTPServer((HOST, PORT), JinjaHandler).serve_forever()
