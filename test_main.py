"""
Unit tests for main.py (adapted for new DAT model and error handling).
"""
import os
import csv
import sys
import tempfile
import pytest
from main import main
from typing import List, Any

def create_csv_file(headers: List[str], rows: List[List[Any]], file_path: str) -> None:
    """Helper to create a CSV file for testing."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def test_main_creativity_score_column(monkeypatch: 'pytest.MonkeyPatch') -> None:
    """
    Test that main() creates the output file with the expected new column and handles creativity score output.
    """
    headers: list[str] = ['test', 'other']
    # Use 7+ valid English words for the DAT model to avoid 'not enough words'
    rows: list[list[str]] = [
        ["cat dog thimble violin tomato jumper tickets", 'bar'],
        ["arm eyes feet hand head leg body", 'baz'],
        ["foo", 'qux']  # Should trigger 'not enough words'
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input.csv')
        create_csv_file(headers, rows, input_path)
        monkeypatch.setattr(sys, 'argv', ['main.py', input_path])
        main()
        output_path = os.path.join(tmpdir, 'input_creativity_score.csv')
        with open(output_path, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
        # Check header
        assert reader[0] == ['test', 'other', 'test_hello']
        # Check for 'not enough words' in last row
        assert reader[3][2] == 'not enough words'
        # Check that the first two rows are floats (creativity scores)
        for i in [1, 2]:
            try:
                float(reader[i][2])
            except ValueError:
                assert False, f"Row {i} does not contain a valid float: {reader[i][2]}"

def test_main_missing_column(monkeypatch: 'pytest.MonkeyPatch', capsys: 'pytest.CaptureFixture[str]') -> None:
    """
    Test that main() prints an error if the required column is missing.
    """
    headers: list[str] = ['not_test', 'other']
    rows: list[list[str]] = [['foo', 'bar']]
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input.csv')
        create_csv_file(headers, rows, input_path)
        monkeypatch.setattr(sys, 'argv', ['main.py', input_path])
        main()
        captured = capsys.readouterr()
        assert "Column 'test' not found in CSV header." in captured.out

def test_main_file_not_found(monkeypatch: 'pytest.MonkeyPatch', capsys: 'pytest.CaptureFixture[str]') -> None:
    """
    Test that main() prints an error if the file does not exist.
    """
    monkeypatch.setattr(sys, 'argv', ['main.py', 'nonexistent.csv'])
    main()
    captured = capsys.readouterr()
    assert "File not found: nonexistent.csv" in captured.out
