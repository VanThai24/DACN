"""
Configuration tests
"""
import pytest
from app.config import settings, is_development, is_production


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings is not None
    assert settings.environment in ["development", "staging", "production"]


def test_jwt_secret_key_exists():
    """Test that JWT secret key is set"""
    assert settings.jwt_secret_key is not None
    assert len(settings.jwt_secret_key) > 10


def test_database_url_exists():
    """Test that database URL is configured"""
    assert settings.database_url is not None
    assert len(settings.database_url) > 0


def test_environment_helpers():
    """Test environment helper functions"""
    if settings.environment == "development":
        assert is_development() is True
        assert is_production() is False
    elif settings.environment == "production":
        assert is_production() is True
        assert is_development() is False


def test_cors_origins_parsed():
    """Test that CORS origins are parsed correctly"""
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0


def test_allowed_extensions_parsed():
    """Test that allowed extensions are parsed correctly"""
    assert isinstance(settings.allowed_extensions, list)
    assert "jpg" in settings.allowed_extensions or "jpeg" in settings.allowed_extensions
