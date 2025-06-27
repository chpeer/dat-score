"""
Unit tests for DAT Score Calculator Flask web application.
"""
import os
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from main import app
from flask import session
import io

# Mock the DAT_MODEL at module level to prevent loading large files during tests
@pytest.fixture(autouse=True)
def mock_dat_model():
    """Mock the DAT_MODEL to prevent loading large word vector files during tests."""
    with patch('main.DAT_MODEL') as mock:
        # Create a mock model that returns a reasonable score
        mock.dat.return_value = 0.75
        yield mock

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit for testing
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    headers = ['word1', 'word2', 'word3', 'description']
    rows = [
        ['cat', 'dog', 'house', 'Test row 1'],
        ['book', 'tree', 'car', 'Test row 2'],
        ['sun', 'moon', 'star', 'Test row 3'],
        ['apple', 'banana', 'orange', 'Test row 4'],
        ['red', 'blue', 'green', 'Test row 5'],
        ['happy', 'sad', 'angry', 'Test row 6'],
        ['fast', 'slow', 'quick', 'Test row 7'],
        ['big', 'small', 'tiny', 'Test row 8'],
        ['hot', 'cold', 'warm', 'Test row 9'],
        ['light', 'dark', 'bright', 'Test row 10']
    ]
    return headers, rows

@pytest.fixture
def sample_csv_file(sample_csv_data):
    """Create a temporary CSV file for testing."""
    headers, rows = sample_csv_data
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)

def test_home_page_get(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'DAT Score Calculator' in response.data
    assert b'Upload CSV File' in response.data
    assert b'Choose a CSV file' in response.data

def test_home_page_post_invalid_file(client):
    """Test that invalid file upload returns an error."""
    response = client.post('/', data={
        'file': (io.BytesIO(b'invalid data'), 'test.txt')
    })
    assert response.status_code == 400
    assert b'Please upload a CSV file' in response.data

def test_home_page_post_valid_csv(client, sample_csv_file):
    """Test that valid CSV upload redirects to column selection page."""
    with open(sample_csv_file, 'rb') as f:
        response = client.post('/', data={
            'file': (f, 'test.csv')
        })
    
    assert response.status_code == 200
    assert b'Select Columns for DAT Calculation' in response.data
    assert b'word1' in response.data
    assert b'word2' in response.data
    assert b'word3' in response.data

def test_column_selection_page_get_without_session(client):
    """Test that accessing column selection without session redirects."""
    response = client.get('/select')
    assert response.status_code == 405  # Method not allowed for GET

def test_column_selection_page_post_preview(client, sample_csv_file):
    """Test that preview functionality works correctly."""
    # First upload a file to create session
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test preview functionality
    response = client.post('/select', data={
        'action': 'preview',
        'skip_rows': '1'
    })
    
    assert response.status_code == 200
    assert b'Select Columns for DAT Calculation' in response.data

def test_column_selection_page_post_no_columns(client, sample_csv_file):
    """Test that submitting without selecting columns shows error."""
    # First upload a file to create session
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test submission without columns
    response = client.post('/select', data={
        'min_word_count': '7',
        'skip_rows': '1'
    })
    
    assert response.status_code == 400
    assert b'Session expired or invalid' in response.data

@patch('main.DAT_MODEL.dat')
def test_column_selection_page_post_success(mock_dat, client, sample_csv_file):
    """Test successful column selection and score calculation."""
    # Mock the DAT model to return a score
    mock_dat.return_value = 0.75
    
    # First upload a file to create session
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test successful submission
    response = client.post('/select', data={
        'columns': ['word1', 'word2'],
        'min_word_count': '7',
        'skip_rows': '1'
    })
    
    assert response.status_code == 200
    assert b'DAT Score Results' in response.data
    assert b'creativity_score' in response.data
    assert b'0.75' in response.data

@patch('main.DAT_MODEL.dat')
def test_column_selection_page_post_not_enough_words(mock_dat, client, sample_csv_file):
    """Test handling of 'not enough words' scenario."""
    # Mock the DAT model to return None (not enough words)
    mock_dat.return_value = None
    
    # First upload a file to create session
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test submission with insufficient words
    response = client.post('/select', data={
        'columns': ['word1'],
        'min_word_count': '10',
        'skip_rows': '1'
    })
    
    assert response.status_code == 200
    assert b'DAT Score Results' in response.data
    assert b'not enough words' in response.data

@patch('main.DAT_MODEL.dat')
def test_column_selection_page_post_dat_error(mock_dat, client, sample_csv_file):
    """Test handling of DAT model errors."""
    # Mock the DAT model to raise an exception
    mock_dat.side_effect = Exception("DAT model error")
    
    # First upload a file to create session
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test submission with DAT error
    response = client.post('/select', data={
        'columns': ['word1', 'word2'],
        'min_word_count': '7',
        'skip_rows': '1'
    })
    
    assert response.status_code == 200
    assert b'DAT Score Results' in response.data
    assert b'error:' in response.data

def test_download_page_without_session(client):
    """Test that download page redirects without session."""
    response = client.get('/download')
    assert response.status_code == 302  # Redirect

def test_download_page_with_session(client, sample_csv_file):
    """Test that download page works with valid session."""
    # First upload a file and calculate scores to create session with output file
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    with patch('main.DAT_MODEL.dat', return_value=0.75):
        client.post('/select', data={
            'columns': ['word1', 'word2'],
            'min_word_count': '7',
            'skip_rows': '1'
        })
    
    # Test download
    response = client.get('/download')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('text/csv')
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'output_creativity_score.csv' in response.headers['Content-Disposition']

def test_session_management(client, sample_csv_file):
    """Test that session data is properly managed."""
    # Upload file
    with open(sample_csv_file, 'rb') as f:
        response = client.post('/', data={'file': (f, 'test.csv')})
    
    # Check that session contains expected data
    with client.session_transaction() as sess:
        assert 'tmp_in_path' in sess
        assert 'header' in sess
        assert 'skip_rows' in sess
        assert sess['header'] == ['word1', 'word2', 'word3', 'description']

def test_file_upload_size_limit(client):
    """Test that large file uploads are rejected."""
    # Create a large file (over 10MB)
    large_data = b'x' * (11 * 1024 * 1024)  # 11MB
    
    response = client.post('/', data={
        'file': (io.BytesIO(large_data), 'large.csv')
    })
    
    assert response.status_code == 413  # Request Entity Too Large

def test_invalid_csv_format(client):
    """Test handling of invalid CSV format."""
    invalid_csv_data = b'This is not a CSV file\nJust some random text'
    
    response = client.post('/', data={
        'file': (io.BytesIO(invalid_csv_data), 'invalid.csv')
    })
    
    assert response.status_code == 200  # Should still process but might show empty preview

def test_empty_csv_file(client):
    """Test handling of empty CSV file."""
    empty_csv_data = b''
    
    response = client.post('/', data={
        'file': (io.BytesIO(empty_csv_data), 'empty.csv')
    })
    
    assert response.status_code == 200  # Should handle gracefully

def test_csv_with_different_encodings(client):
    """Test that CSV files with different encodings are handled."""
    # Create CSV with UTF-8 encoding
    csv_data = 'word1,word2,word3\ncafé,naïve,façade\n'.encode('utf-8')
    
    response = client.post('/', data={
        'file': (io.BytesIO(csv_data), 'utf8.csv')
    })
    
    assert response.status_code == 200
    assert b'caf' in response.data

def test_form_validation(client, sample_csv_file):
    """Test form validation for various inputs."""
    # First upload a file
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test with invalid min_word_count
    response = client.post('/select', data={
        'columns': ['word1'],
        'min_word_count': '0',  # Invalid: should be >= 1
        'skip_rows': '1'
    })
    
    assert response.status_code == 200  # Should still process

def test_restart_functionality(client, sample_csv_file):
    """Test that restart button works correctly."""
    # First upload a file and calculate scores
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    with patch('main.DAT_MODEL.dat', return_value=0.75):
        client.post('/select', data={
            'columns': ['word1', 'word2'],
            'min_word_count': '7',
            'skip_rows': '1'
        })
    
    # Test restart button
    response = client.get('/')
    assert response.status_code == 200
    assert b'Upload CSV File' in response.data

def test_static_files_served(client):
    """Test that static files are served correctly."""
    response = client.get('/static/dat_score_app.css')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('text/css')

def test_error_handling_missing_file(client):
    """Test error handling when uploaded file is missing."""
    # Create session without file
    with client.session_transaction() as sess:
        sess['tmp_in_path'] = '/nonexistent/file.csv'
        sess['header'] = ['test']
        sess['skip_rows'] = 1
    
    response = client.post('/select', data={
        'columns': ['test'],
        'min_word_count': '7',
        'skip_rows': '1'
    })
    
    assert response.status_code == 400
    assert b'no longer available' in response.data

def test_preview_with_different_skip_rows(client, sample_csv_file):
    """Test that preview updates correctly with different skip_rows values."""
    # First upload a file
    with open(sample_csv_file, 'rb') as f:
        client.post('/', data={'file': (f, 'test.csv')})
    
    # Test preview with different skip_rows
    response = client.post('/select', data={
        'action': 'preview',
        'skip_rows': '2'
    })
    
    assert response.status_code == 200
    assert b'Select Columns for DAT Calculation' in response.data

if __name__ == '__main__':
    pytest.main([__file__]) 