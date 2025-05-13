import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)


def setup_test_db():
    """Set up test database with initial data."""
    db = TestingSessionLocal()
    try:
        # Clear existing data
        # Use text() function to wrap raw SQL strings
        db.execute(text("DELETE FROM alerts"))
        db.execute(text("DELETE FROM file_activities"))
        db.execute(text("DELETE FROM login_activities"))
        db.execute(text("DELETE FROM users"))
        
        # Add test users
        admin_password = get_password_hash("adminpass")
        user_password = get_password_hash("userpass")
        
        admin = User(
            email="admin@example.com",
            hashed_password=admin_password,
            full_name="Admin User",
            is_admin=True,
            department="IT"
        )
        user = User(
            email="user@example.com",
            hashed_password=user_password,
            full_name="Regular User",
            is_admin=False,
            department="Sales"
        )
        
        db.add(admin)
        db.add(user)
        db.commit()
        
        return db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# Dependency to override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_db():
    return setup_test_db()


@pytest.fixture
def admin_token():
    response = client.post(
        "/api/v1/login",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token():
    response = client.post(
        "/api/v1/login",
        data={"username": "user@example.com", "password": "userpass"},
    )
    return response.json()["access_token"]


# Actual test functions

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_valid_credentials():
    """Test login with valid credentials"""
    setup_test_db()
    response = client.post(
        "/api/v1/login",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    setup_test_db()
    response = client.post(
        "/api/v1/login",
        data={"username": "admin@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_create_user(admin_token, test_db):
    """Test creating a new user (admin only)"""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "full_name": "New User",
        "department": "Marketing",
        "is_admin": False
    }
    
    response = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "hashed_password" not in data


def test_read_users(admin_token, test_db):
    """Test getting all users (admin only)"""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # At least the admin and regular user should be there


def test_read_users_forbidden_for_regular_user(user_token, test_db):
    """Test that regular users cannot get all users"""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403


def test_read_user_me(user_token, test_db):
    """Test getting the current user info"""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["is_admin"] == False


def test_create_file_activity(user_token, test_db):
    """Test recording file activity"""
    activity_data = {
        "file_path": "/path/to/sensitive/document.pdf",
        "action": "DOWNLOAD",
        "ip_address": "192.168.1.100",
        "device_info": "Windows 10, Chrome 90"
    }
    
    response = client.post(
        "/api/v1/activities/file",
        headers={"Authorization": f"Bearer {user_token}"},
        json=activity_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["file_path"] == activity_data["file_path"]
    assert data["action"] == activity_data["action"]


def test_get_dashboard_data(admin_token, test_db):
    """Test getting dashboard data"""
    response = client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recent_activities" in data
    assert "alerts" in data
    assert "user_stats" in data

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"  # Changed from "ok" to "healthy"