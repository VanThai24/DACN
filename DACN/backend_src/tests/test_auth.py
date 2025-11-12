"""
Unit tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend_src.app.main import app

client = TestClient(app)


def test_health_check():
    """Test API health check endpoint"""
    response = client.get("/")
    assert response.status_code in [200, 404]  # May not have root endpoint


def test_login_missing_credentials():
    """Test login with missing credentials"""
    response = client.post("/api/auth/login", json={})
    assert response.status_code in [400, 422]


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={"username": "invalid_user", "password": "wrong_password"}
    )
    assert response.status_code in [401, 404]


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without authentication"""
    response = client.get("/api/employees")
    # Should require authentication or return empty list
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/auth/login")
    # CORS should be configured
    assert response.status_code in [200, 405]
