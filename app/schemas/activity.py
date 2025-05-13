from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class LoginActivityBase(BaseModel):
    ip_address: str
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    session_id: Optional[str] = None


class LoginActivityCreate(LoginActivityBase):
    user_id: int
    success: bool = True


class LoginActivityUpdate(BaseModel):
    logout_time: Optional[datetime] = None
    is_suspicious: Optional[bool] = None


class LoginActivity(LoginActivityBase):
    id: int
    user_id: int
    timestamp: datetime
    success: bool
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    logout_time: Optional[datetime] = None
    is_unusual_location: bool
    is_unusual_time: bool
    is_suspicious: bool

    class Config:
        orm_mode = True


class FileActivityBase(BaseModel):
    activity_type: str  # download, upload, delete, view
    file_path: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    application: Optional[str] = None
    ip_address: str
    device_info: Optional[str] = None


class FileActivityCreate(FileActivityBase):
    user_id: int
    metadata: Optional[Dict[str, Any]] = None


class FileActivityUpdate(BaseModel):
    is_sensitive_data: Optional[bool] = None
    is_unusual_volume: Optional[bool] = None
    is_unusual_type: Optional[bool] = None
    is_suspicious: Optional[bool] = None


class FileActivity(FileActivityBase):
    id: int
    user_id: int
    timestamp: datetime
    is_sensitive_data: bool
    is_unusual_volume: bool
    is_unusual_type: bool
    is_suspicious: bool
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class AlertBase(BaseModel):
    alert_type: str
    severity: str
    description: str


class AlertCreate(AlertBase):
    user_id: int
    login_activity_id: Optional[int] = None
    file_activity_id: Optional[int] = None


class AlertUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None


class Alert(AlertBase):
    id: int
    timestamp: datetime
    user_id: int
    login_activity_id: Optional[int] = None
    file_activity_id: Optional[int] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None

    class Config:
        orm_mode = True