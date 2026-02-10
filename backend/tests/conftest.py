"""
Pytest configuration and fixtures. Sets a test environment (SQLite + temp dir)
before the app is loaded so tests run without a real database or upload directory.
"""
import os
import sys
import tempfile
from pathlib import Path

# Set test environment before any app import (so get_settings() sees these)
_test_root = tempfile.mkdtemp(prefix="datavisyn_test_")
_test_uploads = os.path.join(_test_root, "uploads")
os.makedirs(_test_uploads, exist_ok=True)
_test_db = os.path.join(_test_root, "test.sqlite")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db}"
os.environ["UPLOAD_DIR"] = _test_uploads

# Ensure backend root is on path so "app" is importable
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base, engine
from app.main import app

# Create tables for the test database
Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    """Test client for the FastAPI app. Uses test DB and temp upload dir."""
    return TestClient(app)
