from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class LoginActivityBase(BaseModel):
    user_email: str
    ip_address: str
    user_agent: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[str] = None
    timestamp: Optional[datetime] = None
    success: bool = True
    is_anomalous: bool = False


class LoginActivityCreate(LoginActivityBase):
    pass


class LoginActivity(LoginActivityBase):
    id: int

    class Config:
        from_attributes = True  # formerly orm_mode


class FileActivityBase(BaseModel):
    user_email: str
    file_path: str
    action: str  # read, write, delete, etc.
    ip_address: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_anomalous: bool = False
    details: Optional[str] = None


class FileActivityCreate(FileActivityBase):
    pass


class FileActivity(FileActivityBase):
    id: int

    class Config:
        from_attributes = True  # formerly orm_mode


class AlertBase(BaseModel):
    alert_type: str
    severity: str
    message: str
    source_ip: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    resolved: Optional[bool] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None


class Alert(AlertBase):
    id: int

    class Config:
        from_attributes = True  # formerly orm_mode