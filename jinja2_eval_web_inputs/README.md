# Input Files

Sample data files for the Jinja2 Web Evaluator.

## Setup

1. Add JSON/YAML files to this directory
2. Configure path in `jinja2_eval_web.conf`:
   ```ini
   [input_files]
   directory = jinja2_eval_web_inputs
   ```
3. Select files via web interface dropdown

## Supported Formats

- **JSON**: Auto-detected format
- **YAML**: Auto-detected format

## Sample Files

- `sample.json` - Server configuration example
- `sample.yaml` - Application data example

## Security

Files outside configured directory cannot be accessed.
