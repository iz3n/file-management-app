"""
Unit tests for file service logic (e.g. count_csv).
Conftest sets test env before any app import, so get_settings() uses test config.
"""
import pytest

from app.services.file_service import count_csv


def test_count_csv_header_only():
    """Header only (one line) gives 0 data rows and column count from header."""
    rows, cols = count_csv(b"a,b,c")
    assert rows == 0
    assert cols == 3


def test_count_csv_single_row():
    """Single header + one data row."""
    rows, cols = count_csv(b"x,y\n1,2")
    assert rows == 1
    assert cols == 2


def test_count_csv_multiple_rows():
    """Multiple data rows."""
    rows, cols = count_csv(b"name,score\nAlice,100\nBob,99")
    assert rows == 2
    assert cols == 2


def test_count_csv_utf8():
    """UTF-8 content is decoded correctly."""
    rows, cols = count_csv("k,v\né,2".encode("utf-8"))
    assert rows == 1
    assert cols == 2
