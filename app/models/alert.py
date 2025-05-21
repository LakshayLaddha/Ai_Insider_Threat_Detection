from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who owns/receives the alert
    alert_type = Column(String)
    severity = Column(String)  # low, medium, high, critical
    message = Column(String)
    source_ip = Column(String)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who resolved the alert
    resolved_at = Column(DateTime, nullable=True)
    
    # Add relationships to match User model
    user = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_alerts")