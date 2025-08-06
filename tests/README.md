# Test Suite Summary

This directory contains comprehensive tests for the Jinja2 Web Evaluator, specifically focused on the new input files functionality and YAML support.

## Test Files Created

### 1. `unit_tests.py`
**Purpose**: Basic endpoint validation
- Tests all server endpoints for correct HTTP status codes
- Validates response formats and error handling
- Quick smoke test to ensure server is functional

**Key Tests**:
- Root page accessibility (200)
- Input files endpoint (empty array when no directory configured)
- Settings endpoints (GET/POST operations)
- History endpoints
- Error handling (404 for invalid endpoints, 400 for missing parameters)

### 2. `workflow_test.py`
**Purpose**: Complete input files workflow validation
- End-to-end testing of input files functionality
- Security testing (path traversal protection)
- Integration testing with rendering

**Key Tests**:
- Configuration management (setting and reading input directory)
- File discovery and listing
- File content reading
- Security validation (prevents path traversal attacks)
- Integration with Jinja2 rendering
- Error condition handling

### 3. `user_simulation.py`
**Purpose**: Realistic user workflow simulation
- Simulates how a real user would interact with the system
- Tests complex real-world scenarios
- Validates complete feature integration

**Key Tests**:
- Creating sample data files (employees, servers, configuration)
- User configuring input directory
- Loading and browsing files through web interface
- Creating complex Jinja2 templates
- Rendering professional reports and configurations
- History tracking validation

### 4. `yaml_support_test.py`
**Purpose**: YAML input format validation
- Tests the new YAML input support functionality
- Validates automatic format detection (JSON vs YAML)
- Tests error handling for invalid inputs

**Key Tests**:
- Valid YAML input parsing and rendering
- Valid JSON input (backward compatibility)
- Invalid input handling (neither JSON nor YAML)
- YAML file loading from input files directory
- Format detection headers verification

### 5. `format_detection_test.py`
**Purpose**: Automatic UI format detection validation
- Tests automatic format detection in combo selectors
- Validates UI updates when content changes
- Tests format detection across different scenarios

**Key Tests**:
- JSON content format detection and UI updates
- YAML content format detection and UI updates
- Plain text content handling
- File loading with automatic format detection
- Result format detection and combo updates

## Test Results Summary

All tests pass successfully, validating:

✅ **Endpoint Functionality**: All HTTP endpoints work correctly with proper status codes
✅ **Configuration Management**: Settings can be saved and retrieved properly
✅ **File Operations**: Files can be listed and content can be read safely
✅ **Security**: Path traversal attacks are prevented (403 errors)
✅ **Integration**: Input files work seamlessly with Jinja2 rendering
✅ **Error Handling**: Proper error responses for various failure scenarios
✅ **User Experience**: Complete workflows function as intended
✅ **History Tracking**: All operations are properly logged
✅ **YAML Support**: Both JSON and YAML inputs are supported with automatic detection
✅ **Format Detection**: UI combos automatically update based on content type

## Security Features Validated

- **Path Traversal Protection**: Prevents access to files outside configured directory
- **Input Sanitization**: Filenames are sanitized to prevent directory traversal
- **Error Handling**: Graceful handling of missing files and configuration errors
- **Access Control**: Only files within the configured directory are accessible

## Production Readiness

The input files functionality is **production ready** with:
- Comprehensive error handling
- Security measures in place
- Full integration with existing features
- Proper configuration management
- Complete test coverage

## Running the Tests

```bash
# Basic endpoint tests (quick)
python3 tests/unit_tests.py

# Complete workflow tests (thorough)
python3 tests/workflow_test.py

# User simulation tests (realistic scenarios)
python3 tests/user_simulation.py

# YAML support tests (new functionality)
python3 tests/yaml_support_test.py

# Format detection tests (UI functionality)
python3 tests/format_detection_test.py
```

All tests should pass with 100% success rate when the server is running on localhost:8000.

## New Features (v1.2)

- **YAML Input Support**: The evaluator now accepts both JSON and YAML input formats
- **Automatic Format Detection**: The server automatically detects whether input is JSON or YAML
- **Format Headers**: Response headers include detected input format information
- **Backward Compatibility**: All existing JSON functionality continues to work unchanged
- **YAML Files**: Input files directory now supports .yaml files alongside .json files
- **Smart UI Updates**: Format combo selectors automatically update based on content type
- **Intelligent Detection**: UI detects format when loading files, history, or manual input
- **Result Format Detection**: Output format is automatically detected and displayed
