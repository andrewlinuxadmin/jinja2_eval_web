# Jinja2 Web Evaluator

A web-based tool for testing and evaluating Jinja2 templates in real-time, specifically designed for Ansible users. This application provides an intuitive interface to test Jinja2 expressions with JSON data and includes all Ansible filters for comprehensive template testing.

![Version](https://img.shields.io/badge/version-1.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Real-time Jinja2 evaluation** with instant results
- **Ansible filters integration** (core, math, and URL filters)
- **Modern web interface** with syntax highlighting
- **Code editors** with syntax highlighting for Jinja2, JSON, and YAML
- **Dark/Light theme support** with customizable settings
- **Expression history** with persistent storage
- **Auto-reload** when source files change
- **Sandboxed environment** for secure template execution
- **Export functionality** for results and configurations

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/andrewlinuxadmin/jinja2_eval_web.git
cd jinja2_eval_web
```

2. Install dependencies:
```bash
pip install -r pip-venv-requirements.txt
```

### Running the Application

Start the web server:
```bash
python jinja2_eval_web.py
```

The application will be available at: http://localhost:8000

## Usage

### Basic Example

1. **JSON Input**: Enter your data in JSON format
```json
{
  "users": [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
  ],
  "environment": "production"
}
```

2. **Jinja2 Expression**: Write your template
```jinja2
Environment: {{ data.environment }}
Users:
{% for user in data.users %}
- {{ user.name }} ({{ user.age }} years old)
{% endfor %}
```

3. **Result**: View the rendered output
```
Environment: production
Users:
- Alice (30 years old)
- Bob (25 years old)
```

### Ansible Filters Example

The application includes all Ansible filters. Try these examples:

```jinja2
{{ data.users | map(attribute='name') | list }}
{{ data.users | selectattr('age', 'gt', 25) | list }}
{{ data.environment | upper }}
```

## API Endpoints

The application provides several REST endpoints:

- `GET /` - Main web interface
- `POST /render` - Evaluate Jinja2 expressions
- `GET /history` - Retrieve evaluation history
- `POST /history/clear` - Clear evaluation history
- `GET /settings` - Get configuration settings
- `POST /settings` - Update configuration settings

### Example API Usage

```bash
# Evaluate a Jinja2 expression
curl -X POST http://localhost:8000/render \
  -d "json={\"name\":\"World\"}" \
  -d "expr=Hello {{ data.name }}!"

# Get history
curl http://localhost:8000/history
```

## Configuration

The application uses a configuration file (`jinja2_eval_web.conf`) to store user preferences:

```ini
[history]
max_entries = 1000

[user]
theme = dark
height-inputcode = 100
height-jinjaexpr = 200
height-resultview = 1000
```

### Configuration Options

- **max_entries**: Maximum number of history entries to keep
- **theme**: UI theme (`dark` or `light`)
- **height-***: Height settings for different editor panels

## Development

### Project Structure

```
jinja2_eval_web/
├── jinja2_eval_web.py          # Main server application
├── jinja2_eval_web.html        # Web interface
├── jinja2_eval_web.conf        # Configuration file
├── jinja2_eval_web.json        # Evaluation history
├── pip-venv-requirements.txt   # Python dependencies
├── tests/                      # Test files
│   ├── test_jinja_2_eval_web.py
│   └── ...
└── README.md                   # This file
```

### Running Tests

```bash
cd tests
python test_jinja_2_eval_web.py
```

You can configure the test server using environment variables:
```bash
export TEST_SERVER_HOST=localhost
export TEST_SERVER_PORT=8000
python test_jinja_2_eval_web.py
```

### Features in Detail

#### Auto-reload
The server automatically reloads when you modify:
- `jinja2_eval_web.py` (main server)
- `jinja2_eval_web.html` (web interface)
- `jinja2_eval_web.conf` (configuration)

#### Security
- Uses Jinja2's `SandboxedEnvironment` for safe template execution
- Prevents access to dangerous Python functions and modules
- All user input is properly validated and escaped

#### History Management
- Automatically saves all evaluations with timestamps
- Base64 encoding for safe storage
- Configurable history size limit
- Easy history browsing and clearing

## Dependencies

- **jinja2**: Template engine
- **ansible-core**: Ansible filters and functionality
- **jmespath**: JSON path expressions
- **httpx**: HTTP client for testing

## Browser Compatibility

- Chrome/Chromium 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/andrewlinuxadmin/jinja2_eval_web/issues)
- **Documentation**: This README and inline code comments
- **Community**: Ansible and Jinja2 communities

## Acknowledgments

- Built with [Jinja2](https://jinja.palletsprojects.com/) templating engine
- Integrates [Ansible](https://www.ansible.com/) filters
- Uses [Bootstrap 5](https://getbootstrap.com/) for UI
- Code editing powered by [CodeMirror](https://codemirror.net/)
