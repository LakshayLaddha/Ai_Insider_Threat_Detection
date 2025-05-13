from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..database import get_db
from ..models.user import User
from ..models.activity import LoginActivity
from ..schemas.user import User as UserSchema
from ..utils.security import verify_password, create_access_token
from ..core.config import settings  # Update to use core.config
from ..services.geoip import geoip_service
from ..services.detection import threat_detection

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def filter_model_fields(model_class, data_dict):
    """Filter dictionary to only include fields that exist in the model"""
    return {k: v for k, v in data_dict.items() if hasattr(model_class, k)}


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Use SECRET_KEY from settings to match what's used in create_access_token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Extract user ID from "data" key instead of "sub"
        user_id = payload.get("data")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        # Add error details for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Only check is_active if that field exists in your User model
    # Comment this out if your User model doesn't have an is_active field
    # if not hasattr(user, 'is_active') or not user.is_active:
    #    raise HTTPException(
    #        status_code=status.HTTP_400_BAD_REQUEST,
    #        detail="Inactive user"
    #    )
    
    return user


def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.post("/login")
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by username
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Record failed login attempt
        client_host = form_data.client.host if hasattr(form_data, 'client') else "unknown"
        
        login_data = {
            "user_id": user.id if user else None,
            "ip_address": client_host,
            "user_agent": form_data.client.headers.get("user-agent") if hasattr(form_data, 'client') else None,
            "success": False
        }
        
        # Add GeoIP information if available
        geo_data = geoip_service.get_location_data(client_host)
        login_data.update(geo_data)
        
        # Filter fields to match the LoginActivity model
        filtered_login_data = filter_model_fields(LoginActivity, login_data)
        
        # Create login activity record for failed attempt
        login_activity = LoginActivity(**filtered_login_data)
        db.add(login_activity)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    user.last_login_at = datetime.now()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=user.id, expires_delta=access_token_expires
    )
    
    # Record successful login
    client_host = form_data.client.host if hasattr(form_data, 'client') else "unknown"
    user_agent = form_data.client.headers.get("user-agent") if hasattr(form_data, 'client') else None
    
    login_data = {
        "user_id": user.id,
        "ip_address": client_host,
        "user_agent": user_agent,
        "session_id": access_token[:8],  # Use first part of token as session ID
        "success": True
    }
    
    # Add GeoIP information
    geo_data = geoip_service.get_location_data(client_host)
    login_data.update(geo_data)
    
    # Check for login anomalies
    anomalies = threat_detection.detect_login_anomalies(db, user.id, login_data)
    login_data.update(anomalies)
    
    # Filter fields to match the LoginActivity model
    filtered_login_data = filter_model_fields(LoginActivity, login_data)
    
    # Create login activity record
    login_activity = LoginActivity(**filtered_login_data)
    db.add(login_activity)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,  # Using email instead of username
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Log out current user by recording logout time.
    """
    # Find active session(s) for this user
    active_sessions = db.query(LoginActivity).filter(
        LoginActivity.user_id == current_user.id,
        LoginActivity.logout_time.is_(None),
        LoginActivity.success == True
    ).order_by(LoginActivity.timestamp.desc()).all()
    
    if active_sessions:
        # Update the most recent session with logout time
        active_sessions[0].logout_time = datetime.now()
        db.commit()
    
    return {"message": "Successfully logged out"}