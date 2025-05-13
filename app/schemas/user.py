from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None  # Make username optional to support existing users
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_admin: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    profile_image: Optional[str] = None


# Additional properties to return via API
class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Properties for admin user management
class AdminUserUpdate(UserUpdate):
    pass


# Add UserInList class that was missing
class UserInList(User):
    # This class inherits all fields from User
    # Could be extended with additional fields specific for list responses
    pass