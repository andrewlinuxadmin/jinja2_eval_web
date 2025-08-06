# Input Files Directory

This directory contains JSON files that can be loaded into the Jinja2 Web Evaluator.

## Usage

1. Place your JSON files in this directory
2. Configure the input files directory in the web interface (Settings tab)
3. Select files from the Input Files dropdown in the web interface
4. Files will be automatically loaded into the JSON input field

## File Format

All files should be valid JSON format. Examples:

```json
{
  "users": [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"}
  ]
}
```

## Security

- Only files within this configured directory can be accessed
- Path traversal attacks are prevented
- Only valid filenames are accepted

## Example Files

- `sample.json` - Example configuration and server data
