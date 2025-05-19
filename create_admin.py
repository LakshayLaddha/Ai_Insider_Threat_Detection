from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import sys

# Add the project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Try to import from the app, but fall back to defining directly if needed
try:
    from app.utils.security import get_password_hash
except ImportError:
    import hashlib
    import bcrypt
    
    def get_password_hash(password: str) -> str:
        """Create password hash using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode('utf-8')

# Database connection - adjust as needed for your setup
try:
    from app.database import engine, SessionLocal, Base
except ImportError:
    # Direct database connection if imports fail
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sentinel.db"  # Change this to your actual DB URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

# Simple User model (minimal definition)
class SimpleUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create the admin user
def create_admin():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Start a session
    db = SessionLocal()
    
    # Check if admin already exists
    admin_email = "admin@example.com"
    existing_user = db.query(SimpleUser).filter(SimpleUser.email == admin_email).first()
    
    if existing_user:
        print(f"Admin user already exists: {existing_user.username} (ID: {existing_user.id})")
        print(f"Email: {existing_user.email}")
        print("Password remains unchanged")
        
        # Optional: Reset password for existing user
        new_password = "Admin@123"
        existing_user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"Password reset to: {new_password}")
    else:
        # Create new admin user
        new_password = "Admin@123"
        admin_user = SimpleUser(
            email=admin_email,
            username="admin",
            hashed_password=get_password_hash(new_password),
            full_name="Admin User",
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Created admin user: {admin_user.username} (ID: {admin_user.id})")
        print(f"Email: {admin_user.email}")
        print(f"Password: {new_password}")
    
    db.close()

if __name__ == "__main__":
    create_admin()
    print("\nYou can now login with these credentials on your frontend.")