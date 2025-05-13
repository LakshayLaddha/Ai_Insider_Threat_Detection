from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class LoginActivity(Base):
    __tablename__ = "login_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String)
    user_agent = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    # Add missing geolocation fields
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    is_suspicious = Column(Boolean, default=False)
    risk_score = Column(Integer, default=0)
    session_id = Column(String, nullable=True)

    # Add the missing relationship for alerts
    user = relationship("User", back_populates="login_activities")
    alerts = relationship("Alert", back_populates="login_activity")


class FileActivity(Base):
    __tablename__ = "file_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=func.now())
    file_path = Column(String)
    file_name = Column(String)
    activity_type = Column(String)  # DOWNLOAD, UPLOAD, DELETE, VIEW
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    is_suspicious = Column(Boolean, default=False)
    risk_score = Column(Integer, default=0)

    user = relationship("User", back_populates="file_activities")
    alerts = relationship("Alert", back_populates="file_activity")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=func.now())
    alert_type = Column(String)  # login, file, behavior
    description = Column(Text)
    severity = Column(String)  # low, medium, high, critical
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    login_activity_id = Column(Integer, ForeignKey("login_activities.id", ondelete="SET NULL"), nullable=True)
    file_activity_id = Column(Integer, ForeignKey("file_activities.id", ondelete="SET NULL"), nullable=True)

    # Define relationships with consistent back_populates references
    user = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_alerts")
    login_activity = relationship("LoginActivity", back_populates="alerts")
    file_activity = relationship("FileActivity", back_populates="alerts")