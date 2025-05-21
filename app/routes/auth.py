from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..database import get_db
from ..models.user import User
from ..models.activity import LoginActivity
from ..models.alert import Alert  # Add import for Alert model
from ..schemas.user import User as UserSchema
from ..utils.security import verify_password, create_access_token
from ..core.config import settings  
from ..services.detection import threat_detection  # Import only once
from ..services.geoip import geoip_service

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
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("data")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
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
    request: Request,  # Add request parameter to get client info
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        # Find user by username
        user = db.query(User).filter(User.email == form_data.username).first()
        
        # Get client information from request
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Check if user exists and password is correct
        if not user or not verify_password(form_data.password, user.hashed_password):
            # Record failed login attempt
            login_data = {
                "user_id": user.id if user else None,
                "user_email": form_data.username,  # Always record the attempted email
                "ip_address": client_host,
                "user_agent": user_agent,
                "success": False
            }
            
            # Add GeoIP information if available
            try:
                geo_data = geoip_service.get_location_data(client_host)
                login_data.update(geo_data)
            except Exception as e:
                pass  # Ignore GeoIP errors on failed login
            
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
        login_data = {
            "user_id": user.id,
            "user_email": user.email,
            "ip_address": client_host,
            "user_agent": user_agent,
            "success": True
        }
        
        # Add GeoIP information
        try:
            geo_data = geoip_service.get_location_data(client_host)
            login_data.update(geo_data)
        except Exception as e:
            pass  # Don't fail login if GeoIP fails
        
        # Check for login anomalies
        try:
            anomalies = threat_detection.detect_login_anomalies(db, user.id, login_data)
            
            # Create alert if suspicious activity was detected
            if anomalies.get("is_suspicious", False):
                should_create, severity, description = threat_detection.should_create_alert(anomalies)
                if should_create:
                    alert = Alert(
                        user_id=user.id,
                        alert_type="login",
                        severity=severity,
                        message=description,
                        source_ip=client_host,
                        location=login_data.get("country", "Unknown")
                    )
                    db.add(alert)
                    db.commit()
        except Exception as e:
            # Don't fail login if anomaly detection fails
            pass
        
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
                "email": user.email,
                "full_name": user.full_name if hasattr(user, 'full_name') else "",
                "is_admin": user.is_admin
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions as they are legitimate auth failures
        raise
    except Exception as e:
        # Log the error but return a generic auth failure message
        print(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Log out current user.
    """
    # Return a success message (no need to update login activity if your model doesn't have logout_time)
    return {"message": "Successfully logged out"}