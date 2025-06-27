# Testing Guide for DAT Score Calculator

This document explains how to run tests for the DAT Score Calculator web application and what functionality is covered.

## 🧪 Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Or run with pytest directly
poetry run pytest test_main.py -v
```

### Prerequisites
```bash
# Install dependencies using Poetry
poetry install

# Install additional test dependencies (if needed)
poetry add --group dev pytest pytest-cov

# Optional: Install coverage for detailed reports
poetry add --group dev coverage
```

## 📋 Test Coverage

The test suite covers all major functionality of the web application:

### 🔗 Route Testing
- **Home Page (`/`)**
  - GET request loads upload form correctly
  - POST with invalid file returns error
  - POST with valid CSV redirects to column selection

- **Column Selection (`/select`)**
  - GET request returns 405 (Method Not Allowed)
  - POST with preview action updates table
  - POST without columns shows error
  - POST with valid data calculates scores

- **Download (`/download`)**
  - GET without session redirects
  - GET with session returns CSV file

### 📁 File Upload Testing
- **Valid CSV files** - Proper processing and preview
- **Invalid file types** - Error handling for non-CSV files
- **File size limits** - Rejection of files over 10MB
- **Empty files** - Graceful handling of empty CSV
- **Different encodings** - UTF-8 support
- **Malformed CSV** - Handling of invalid CSV format

### 🧮 DAT Model Testing
- **Successful calculations** - Valid creativity scores returned
- **Insufficient words** - "not enough words" handling
- **Model errors** - Exception handling and error display
- **Mock testing** - Isolated testing without loading full model

### 🔄 Session Management
- **Session creation** - Proper session data storage
- **Session validation** - Error handling for expired sessions
- **File persistence** - Temporary file management
- **Session cleanup** - Proper resource management

### 📝 Form Validation
- **Required fields** - Column selection validation
- **Input validation** - Min word count, skip rows
- **Preview functionality** - Dynamic table updates
- **Form submission** - Complete workflow testing

### 🎨 UI/UX Testing
- **Static files** - CSS and assets served correctly
- **Restart functionality** - Navigation back to upload
- **Error messages** - User-friendly error display
- **Responsive design** - Mobile compatibility

## 🏃‍♂️ Running Specific Tests

### Run Individual Test Functions
```bash
# Run specific test
poetry run pytest test_main.py::test_home_page_get -v

# Run tests matching pattern
poetry run pytest test_main.py -k "upload" -v

# Run tests with coverage
poetry run pytest test_main.py --cov=main --cov-report=html
```

### Test Categories
```bash
# Route tests only
poetry run pytest test_main.py -k "test_home_page" -v

# File upload tests only
poetry run pytest test_main.py -k "file" -v

# DAT model tests only
poetry run pytest test_main.py -k "dat" -v

# Session tests only
poetry run pytest test_main.py -k "session" -v
```

## 📊 Coverage Reports

### Generate Coverage Report
```bash
# Terminal coverage report
poetry run pytest test_main.py --cov=main --cov-report=term-missing

# HTML coverage report
poetry run pytest test_main.py --cov=main --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Targets
- **Routes**: 100% - All endpoints tested
- **File handling**: 100% - Upload, processing, download
- **Error handling**: 100% - All error scenarios covered
- **Session management**: 100% - Session lifecycle tested

## 🔧 Test Configuration

### Environment Variables
```bash
# Set test environment
export FLASK_ENV=testing
export SECRET_KEY=test-secret-key

# Or use Poetry's environment management
poetry run --env FLASK_ENV=testing --env SECRET_KEY=test-secret-key python run_tests.py
```

### Test Fixtures
- **`client`** - Flask test client with proper configuration
- **`sample_csv_data`** - Test data for CSV files
- **`sample_csv_file`** - Temporary CSV file for testing

### Mock Objects
- **`DAT_MODEL.dat`** - Mocked to avoid loading full model
- **File operations** - Isolated testing without file system dependencies

## 🐛 Debugging Tests

### Verbose Output
```bash
# Maximum verbosity
poetry run pytest test_main.py -vvv

# Show local variables on failure
poetry run pytest test_main.py --tb=long
```

### Debug Mode
```bash
# Run with debugger
poetry run pytest test_main.py --pdb

# Stop on first failure
poetry run pytest test_main.py -x
```

### Test Isolation
```bash
# Run tests in isolation
poetry run pytest test_main.py --dist=no

# Clean up after each test
poetry run pytest test_main.py --setup-show
```

## 📝 Adding New Tests

### Test Structure
```python
def test_new_functionality(client):
    """Test description."""
    # Arrange
    # Act
    response = client.post('/endpoint', data={...})
    # Assert
    assert response.status_code == 200
    assert b'expected content' in response.data
```

### Test Naming Convention
- `test_route_name_action` - Route testing
- `test_feature_name_scenario` - Feature testing
- `test_error_condition` - Error handling
- `test_edge_case` - Edge case testing

### Best Practices
1. **Use descriptive names** - Clear test purpose
2. **Test one thing** - Single assertion per test
3. **Use fixtures** - Reusable test data
4. **Mock external dependencies** - Isolate unit tests
5. **Clean up resources** - Proper teardown

## 🚀 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: latest
          virtualenvs-create: true
          virtualenvs-in-project: true
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run python run_tests.py
```

## 📈 Performance Testing

### Load Testing (Optional)
```bash
# Install locust for load testing
poetry add --group dev locust

# Run load test
poetry run locust -f locustfile.py --host=http://localhost:5000
```

### Memory Testing
```bash
# Install memory profiler
poetry add --group dev memory-profiler

# Monitor memory usage during tests
poetry run python -m memory_profiler run_tests.py
```

## 🔍 Test Maintenance

### Regular Tasks
- **Update test data** - Keep sample CSV files current
- **Review coverage** - Ensure new features are tested
- **Update mocks** - Keep mock objects synchronized
- **Performance monitoring** - Track test execution time

### Test Data Management
- **Sample files** - Maintain realistic test data
- **Edge cases** - Include boundary conditions
- **Error scenarios** - Test failure modes
- **Internationalization** - Test with different encodings

### Poetry Commands for Development
```bash
# Add new test dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Run tests in Poetry environment
poetry run python run_tests.py

# Activate Poetry shell for development
poetry shell
```

## 🛠️ Development Setup

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd dat-score

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Run tests to verify setup
poetry run python run_tests.py
```

### Adding New Dependencies
```bash
# Add runtime dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Add optional dependency
poetry add --group optional package-name
```

---

For more information about testing Flask applications, see the [Flask Testing Documentation](https://flask.palletsprojects.com/en/2.3.x/testing/).

For Poetry documentation, see the [Poetry Documentation](https://python-poetry.org/docs/). 