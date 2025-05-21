from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    source_ip: Optional[str] = None
    location: Optional[str] = None

class AlertCreate(AlertBase):
    timestamp: datetime

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime
    resolved: bool
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True