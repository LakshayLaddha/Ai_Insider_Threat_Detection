from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import User as UserSchema
from ..schemas.user import UserCreate, UserUpdate, UserInList
from ..utils.security import get_password_hash
from .auth import get_current_user, get_current_active_admin

router = APIRouter()


@router.get("/", response_model=List[UserInList])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Retrieve users. Admin only.
    """
    # Build query with filters
    query = db.query(User)
    
    if department:
        query = query.filter(User.department == department)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
        
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    
    # Ensure username field is populated for schema validation
    for user in users:
        if not user.username:
            user.username = user.email.split('@')[0]  # Use email prefix as username if missing
    
    return users


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Create new user. Admin only.
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    
    # Generate username if not provided
    username = user_in.username
    if not username:
        username = user_in.email.split('@')[0]
        
    # Create new user
    user = User(
        email=user_in.email,
        username=username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        department=user_in.department,
        role=user_in.role,
        is_admin=user_in.is_admin,
        is_active=user_in.is_active if user_in.is_active is not None else True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    # Ensure username is populated for schema validation
    if not current_user.username:
        current_user.username = current_user.email.split('@')[0]
        db.add(current_user)
        db.commit()
        
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get user by ID.
    """
    # Regular users can only access their own info
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    # Ensure username is populated for schema validation
    if not user.username:
        user.username = user.email.split('@')[0]
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(...),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a user.
    Regular users can only update their own info. Admins can update any user.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )
    
    # Get user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    # Update user data from input model
    update_data = user_in.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Regular users can't change admin status
    if not current_user.is_admin and "is_admin" in update_data:
        del update_data["is_admin"]
    
    # Apply updates
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Ensure username is set if empty
    if not user.username:
        user.username = user.email.split('@')[0]
        
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(...),
    current_user: User = Depends(get_current_active_admin),
) -> None:
    """
    Delete a user. Admin only.
    """
    # Get user to delete
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own user account",
        )
    
    db.delete(user)
    db.commit()