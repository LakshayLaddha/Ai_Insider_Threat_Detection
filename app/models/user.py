from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)  # Add username field
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    department = Column(String, nullable=True)
    role = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    profile_image = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    # Add complementary back_populates relationships
    login_activities = relationship("LoginActivity", back_populates="user")
    file_activities = relationship("FileActivity", back_populates="user")
    alerts = relationship("Alert", back_populates="user", foreign_keys="Alert.user_id")
    resolved_alerts = relationship("Alert", back_populates="resolver", foreign_keys="Alert.resolved_by")