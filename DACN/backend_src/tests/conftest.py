"""
Test configuration for pytest
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from backend_src.app.main import app
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "password": "testpassword123",
        "email": "test@example.com"
    }


@pytest.fixture
def test_employee_data():
    """Sample employee data for testing"""
    return {
        "name": "Test Employee",
        "phone": "0123456789",
        "email": "employee@example.com",
        "role": "employee"
    }
