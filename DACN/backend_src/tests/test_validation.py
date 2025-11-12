"""
Tests for input validation
"""
import pytest
from backend_src.app.schemas.employee import EmployeeCreate, EmployeeUpdate
from backend_src.app.schemas.auth import UserLogin, UserRegister, PasswordChange
from pydantic import ValidationError


class TestEmployeeValidation:
    """Test employee schema validation"""
    
    def test_valid_employee_creation(self):
        """Test valid employee data"""
        employee = EmployeeCreate(
            name="John Doe",
            phone="0123456789",
            email="john@example.com",
            role="employee"
        )
        assert employee.name == "John Doe"
        assert employee.phone == "0123456789"
        assert employee.role == "employee"
    
    def test_invalid_name_too_short(self):
        """Test name validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(name="A", phone="0123456789")
        assert "at least 2 characters" in str(exc_info.value).lower()
    
    def test_invalid_phone_format(self):
        """Test phone validation - invalid format"""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(name="John Doe", phone="abc123")
        assert "invalid phone" in str(exc_info.value).lower()
    
    def test_invalid_email(self):
        """Test email validation"""
        with pytest.raises(ValidationError):
            EmployeeCreate(
                name="John Doe",
                email="invalid-email"
            )
    
    def test_invalid_role(self):
        """Test role validation"""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(
                name="John Doe",
                role="invalid_role"
            )
        assert "role must be one of" in str(exc_info.value).lower()
    
    def test_phone_normalization(self):
        """Test phone number normalization"""
        employee = EmployeeCreate(
            name="John Doe",
            phone="012 345-6789"
        )
        # Should remove spaces and dashes
        assert "-" not in employee.phone
        assert " " not in employee.phone


class TestAuthValidation:
    """Test authentication schema validation"""
    
    def test_valid_login(self):
        """Test valid login credentials"""
        login = UserLogin(
            username="testuser",
            password="password123"
        )
        assert login.username == "testuser"
        assert login.password == "password123"
    
    def test_invalid_username_too_short(self):
        """Test username validation - too short"""
        with pytest.raises(ValidationError):
            UserLogin(username="ab", password="password123")
    
    def test_invalid_password_too_short(self):
        """Test password validation - too short"""
        with pytest.raises(ValidationError):
            UserLogin(username="testuser", password="12345")
    
    def test_invalid_username_characters(self):
        """Test username validation - invalid characters"""
        with pytest.raises(ValidationError):
            UserLogin(username="test@user!", password="password123")
    
    def test_valid_registration(self):
        """Test valid user registration"""
        user = UserRegister(
            username="newuser",
            password="password123",
            email="user@example.com"
        )
        assert user.username == "newuser"
        assert user.email == "user@example.com"
    
    def test_password_change_same_password(self):
        """Test password change - new password same as old"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(
                old_password="password123",
                new_password="password123"
            )
        assert "different" in str(exc_info.value).lower()


class TestFieldValidation:
    """Test individual field validators"""
    
    def test_name_strips_whitespace(self):
        """Test name validation strips whitespace"""
        employee = EmployeeCreate(name="  John Doe  ")
        assert employee.name == "John Doe"
    
    def test_empty_name_rejected(self):
        """Test empty name is rejected"""
        with pytest.raises(ValidationError):
            EmployeeCreate(name="   ")
    
    def test_role_case_insensitive(self):
        """Test role validation is case-insensitive"""
        employee = EmployeeCreate(name="John", role="EMPLOYEE")
        assert employee.role == "employee"
    
    def test_international_phone(self):
        """Test international phone format"""
        employee = EmployeeCreate(
            name="John Doe",
            phone="+84123456789"
        )
        assert employee.phone.startswith("+84")
