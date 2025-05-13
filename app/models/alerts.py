from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .activity import Alert  # Reexport Alert from activity

from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    alert_type = Column(String, index=True)
    severity = Column(String)
    message = Column(Text)
    details = Column(Text)
    source_ip = Column(String)
    is_resolved = Column(Boolean, default=False)
    resolution_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Changed from created_by to user_id to match what routes are using
    user_id = Column(Integer, ForeignKey("users.id"))
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Updated relationships to match field names
    user = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_alerts")