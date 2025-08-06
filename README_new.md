# Jinja2 Web Evaluator

A web-based tool for testing Jinja2 templates in real-time with Ansible filters support.

![Version](https://img.shields.io/badge/version-1.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Real-time Jinja2 evaluation** with instant results
- **Ansible filters** (200+ filters including core, math, and URL filters)
- **JSON/YAML support** with automatic format detection
- **Syntax highlighting** for Jinja2, JSON, YAML, and XML
- **Input files** - Load data from local files
- **Download buttons** with smart file extensions
- **History tracking** with persistent storage
- **Dark/Light themes** and customizable settings
- **Auto-reload** development mode

## Quick Start

### Prerequisites
- Python 3.9+

### Installation & Running
```bash
git clone https://github.com/andrewlinuxadmin/jinja2_eval_web.git
cd jinja2_eval_web
pip install -r pip-venv-requirements.txt
python jinja2_eval_web.py
```

Access at: http://localhost:8000

## Basic Usage

1. **JSON/YAML Input**: Enter your data
```json
{"users": [{"name": "Alice", "age": 30}], "env": "prod"}
```

2. **Jinja2 Template**: Write your expression
```jinja2
Environment: {{ data.env }}
{% for user in data.users %}
- {{ user.name }} ({{ user.age }} years old)
{% endfor %}
```

3. **Result**: View rendered output
```
Environment: prod
- Alice (30 years old)
```

## Input Files

Configure input files directory in `jinja2_eval_web.conf`:
```ini
[input_files]
directory = ./data
```

Place JSON/YAML files in the directory and load them via the web interface.

## Testing

```bash
# Run all tests
cd tests
python unit_tests.py
python button_layout_test.py  
python dynamic_extensions_test.py
```

## Configuration

Edit `jinja2_eval_web.conf`:
```ini
[history]
max_entries = 1000

[input_files]
directory = jinja2_eval_web_inputs

[user]
theme = dark
```

## API Endpoints

- `GET /` - Main interface
- `POST /render` - Evaluate templates  
- `GET /input-files` - List input files
- `GET /history` - Get evaluation history
- `GET /settings` - Get/update settings

## Project Structure

```
jinja2_eval_web/
├── jinja2_eval_web.py      # Main server
├── jinja2_eval_web.html    # Web interface  
├── jinja2_eval_web.conf    # Configuration
├── pip-venv-requirements.txt
├── jinja2_eval_web_inputs/ # Sample input files
└── tests/                  # Test suite
```

## Dependencies

- **jinja2** - Template engine
- **ansible-core** - Ansible filters
- **PyYAML** - YAML support

## License

MIT License - see [LICENSE](LICENSE) file.
