from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class LoginActivity(Base):
    __tablename__ = "login_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Foreign key to users table
    user_email = Column(String, index=True)  # Add this column
    ip_address = Column(String)
    user_agent = Column(String)
    country = Column(String)
    city = Column(String)
    coordinates = Column(String, nullable=True)  # Stored as "lat,lng" format
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    is_anomalous = Column(Boolean, default=False)
    
    # Add relationship back to user
    user = relationship("User", back_populates="login_activities")

class FileActivity(Base):
    __tablename__ = "file_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Foreign key to users table
    user_email = Column(String, index=True)  # Add this column
    file_path = Column(String)
    action = Column(String)  # read, write, delete, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    is_anomalous = Column(Boolean, default=False)
    details = Column(Text, nullable=True)  # Additional details about the activity
    
    # Add relationship back to user
    user = relationship("User", back_populates="file_activities")