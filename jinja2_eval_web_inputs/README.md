# Input Files Directory

This directory contains JSON and YAML files that can be loaded into the Jinja2 Web Evaluator.

## Usage

1. Place your JSON or YAML files in this directory
2. Configure the input files directory in the web interface (Settings tab)
3. Select files from the Input Files dropdown in the web interface
4. Files will be automatically loaded into the input field

## File Formats

The evaluator supports both JSON and YAML formats with automatic detection:

### JSON Example:
```json
{
  "users": [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"}
  ]
}
```

### YAML Example:
```yaml
users:
  - name: Alice
    role: admin
  - name: Bob
    role: user
```

## Security

- Only files within this configured directory can be accessed
- Path traversal attacks are prevented
- Only valid filenames are accepted

## Example Files

- `sample.json` - Example JSON configuration and server data
- `sample.yaml` - Example YAML configuration with applications data
