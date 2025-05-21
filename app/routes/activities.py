# Change this line at the top of your file:
from ..models.activity import LoginActivity, FileActivity
from app.models.alert import Alert  # Use absolute import

from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.user import User

from ..schemas.activity import (
    LoginActivity as LoginActivitySchema,
    LoginActivityCreate, 
    FileActivity as FileActivitySchema,
    FileActivityCreate,
    Alert as AlertSchema,
    AlertCreate,
    AlertUpdate
)
from .auth import get_current_user, get_current_active_admin
from ..services.detection import threat_detection
from ..services.geoip import geoip_service  # Make sure this matches your IPinfo service name

router = APIRouter()

# === Login Activity Routes ===

@router.get("/logins", response_model=List[LoginActivitySchema])
def read_login_activities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    is_suspicious: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve login activities.
    Regular users can only see their own activities.
    Admins can see all activities and filter by user_id.
    """
    # Base query
    query = db.query(LoginActivity)
    
    # Handle user permissions
    if not current_user.is_admin:
        # Regular users can only see their own activities
        query = query.filter(LoginActivity.user_id == current_user.id)
    elif user_id:
        # Admin filtering by specific user
        query = query.filter(LoginActivity.user_id == user_id)
    
    # Apply date filters
    if from_date:
        query = query.filter(LoginActivity.timestamp >= from_date)
    if to_date:
        query = query.filter(LoginActivity.timestamp <= to_date)
    
    # Apply suspicious filter
    if is_suspicious is not None:
        query = query.filter(LoginActivity.is_suspicious == is_suspicious)
    
    # Order and paginate
    activities = query.order_by(LoginActivity.timestamp.desc()).offset(skip).limit(limit).all()
    
    return activities


@router.post("/logins", response_model=LoginActivitySchema)
def create_login_activity(
    *,
    db: Session = Depends(get_db),
    activity_in: LoginActivityCreate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Create new login activity record.
    Admin access only.
    """
    # Add IPinfo information (assuming your IPinfo service is named geoip_service)
    geo_data = geoip_service.get_location_data(activity_in.ip_address)
    
    # Create activity object
    activity_data = activity_in.dict()
    activity_data.update(geo_data)
    
    # Check for anomalies
    anomalies = threat_detection.detect_login_anomalies(db, activity_in.user_id, activity_data)
    activity_data.update(anomalies)
    
    # Create and save activity
    db_activity = LoginActivity(**activity_data)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Check if alert should be created
    should_create, severity, description = threat_detection.should_create_alert(anomalies)
    if should_create:
        alert = Alert(
            user_id=activity_in.user_id,
            alert_type="login",
            severity=severity,
            description=description,
            login_activity_id=db_activity.id,
        )
        db.add(alert)
        db.commit()
    
    return db_activity


# === File Activity Routes ===

@router.get("/files", response_model=List[FileActivitySchema])
def read_file_activities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    activity_type: Optional[str] = None,
    is_suspicious: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve file activities.
    Regular users can only see their own activities.
    Admins can see all activities and filter by user_id.
    """
    # Base query
    query = db.query(FileActivity)
    
    # Handle user permissions
    if not current_user.is_admin:
        # Regular users can only see their own activities
        query = query.filter(FileActivity.user_id == current_user.id)
    elif user_id:
        # Admin filtering by specific user
        query = query.filter(FileActivity.user_id == user_id)
    
    # Apply date filters
    if from_date:
        query = query.filter(FileActivity.timestamp >= from_date)
    if to_date:
        query = query.filter(FileActivity.timestamp <= to_date)
    
    # Apply type filter
    if activity_type:
        query = query.filter(FileActivity.activity_type == activity_type)
    
    # Apply suspicious filter
    if is_suspicious is not None:
        query = query.filter(FileActivity.is_suspicious == is_suspicious)
    
    # Order and paginate
    activities = query.order_by(FileActivity.timestamp.desc()).offset(skip).limit(limit).all()
    
    return activities


# Add the file endpoint that's missing in tests
@router.post("/file", status_code=201)
def create_file_activity_simple(
    activity_in: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Create new file activity record with simplified input.
    This matches the endpoint expected in your tests.
    """
    # Create activity data from input
    activity_data = {
        "user_id": current_user.id,
        "file_path": activity_in.get("file_path"),
        "activity_type": activity_in.get("action", "VIEW"),
        "ip_address": activity_in.get("ip_address"),
        "device_info": activity_in.get("device_info"),
        "file_name": activity_in.get("file_path", "").split("/")[-1] if "/" in activity_in.get("file_path", "") else activity_in.get("file_path", "")
    }
    
    # Create and save activity
    db_activity = FileActivity(**activity_data)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Return a simple dictionary to match test expectations
    return {
        "id": db_activity.id,
        "user_id": db_activity.user_id,
        "file_path": db_activity.file_path,
        "action": db_activity.activity_type,  # Map activity_type to action for test expectation
        "ip_address": db_activity.ip_address,
        "device_info": db_activity.device_info,
        "file_name": db_activity.file_name,
        "timestamp": db_activity.timestamp
    }


@router.post("/files", response_model=FileActivitySchema)
def create_file_activity(
    *,
    db: Session = Depends(get_db),
    activity_in: FileActivityCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new file activity record.
    """
    # Ensure user is creating an activity for themselves unless admin
    if activity_in.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create activities for your own account",
        )
    
    # Create activity object
    activity_data = activity_in.dict()
    
    # Check for anomalies
    activity_obj = FileActivity(**activity_data)
    anomalies = threat_detection.detect_file_anomalies(db, activity_in.user_id, activity_obj)
    activity_data.update(anomalies)
    
    # Create and save activity
    db_activity = FileActivity(**activity_data)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Check if alert should be created
    should_create, severity, description = threat_detection.should_create_alert(anomalies)
    if should_create:
        alert = Alert(
            user_id=activity_in.user_id,
            alert_type="file",
            severity=severity,
            description=description,
            file_activity_id=db_activity.id,
        )
        db.add(alert)
        db.commit()
    
    return db_activity


# === Alerts Routes ===

@router.get("/alerts", response_model=List[AlertSchema])
def read_alerts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    is_resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve alerts.
    Regular users can only see their own alerts.
    Admins can see all alerts and filter by user_id.
    """
    # Base query
    query = db.query(Alert)
    
    # Handle user permissions
    if not current_user.is_admin:
        # Regular users can only see their own alerts
        query = query.filter(Alert.user_id == current_user.id)
    elif user_id:
        # Admin filtering by specific user
        query = query.filter(Alert.user_id == user_id)
    
    # Apply date filters
    if from_date:
        query = query.filter(Alert.timestamp >= from_date)
    if to_date:
        query = query.filter(Alert.timestamp <= to_date)
    
    # Apply resolved filter
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    
    # Apply severity filter
    if severity:
        query = query.filter(Alert.severity == severity)
    
    # Order and paginate
    alerts = query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    
    return alerts


@router.post("/alerts", response_model=AlertSchema)
def create_alert(
    *,
    db: Session = Depends(get_db),
    alert_in: AlertCreate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Create new alert manually.
    Admin access only.
    """
    db_alert = Alert(**alert_in.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.put("/alerts/{alert_id}", response_model=AlertSchema)
def update_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    alert_in: AlertUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update an alert (e.g., resolve it).
    Regular users can only update their own alerts.
    Admins can update any alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Check permissions
    if not current_user.is_admin and alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update alert
    update_data = alert_in.dict(exclude_unset=True)
    
    # If resolving the alert and resolved_by is not set, set it to current user
    if update_data.get("is_resolved") and not update_data.get("resolved_by"):
        update_data["resolved_by"] = current_user.id
        update_data["resolved_at"] = datetime.now()
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# Add dashboard endpoint that's expected in tests
@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Get aggregated data for dashboard.
    This matches the endpoint expected in your tests.
    """
    result = {}
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query filters
    login_query = db.query(LoginActivity).filter(LoginActivity.timestamp >= start_date)
    file_query = db.query(FileActivity).filter(FileActivity.timestamp >= start_date)
    alert_query = db.query(Alert).filter(Alert.timestamp >= start_date)
    
    # Activity counts
    result["total_logins"] = login_query.count()
    result["total_file_activities"] = file_query.count()
    result["total_alerts"] = alert_query.count()
    result["unresolved_alerts"] = alert_query.filter(Alert.is_resolved == False).count()
    
    # File activity breakdown by type
    file_types = db.query(
        FileActivity.activity_type,
        func.count(FileActivity.id).label("count")
    ).filter(
        FileActivity.timestamp >= start_date
    )
    
    result["file_activity_types"] = {
        r[0]: r[1] for r in file_types.group_by(FileActivity.activity_type).all()
    }
    
    # Alert severity breakdown
    alert_severity = db.query(
        Alert.severity,
        func.count(Alert.id).label("count")
    ).filter(
        Alert.timestamp >= start_date
    )
    
    result["alert_severity"] = {
        r[0]: r[1] for r in alert_severity.group_by(Alert.severity).all()
    }
    
    # Most active users (admin only)
    active_users = db.query(
        FileActivity.user_id,
        func.count(FileActivity.id).label("activity_count")
    ).filter(
        FileActivity.timestamp >= start_date
    ).group_by(
        FileActivity.user_id
    ).order_by(
        func.count(FileActivity.id).desc()
    ).limit(5).all()
    
    result["most_active_users"] = []
    for user_id, count in active_users:
        user = db.query(User).get(user_id)
        if user:
            result["most_active_users"].append({
                "user_id": user_id,
                "username": user.username,
                "activity_count": count
            })
    
    # Add recent activities key to match test expectations
    recent_logins = db.query(LoginActivity).order_by(LoginActivity.timestamp.desc()).limit(10).all()
    recent_file_activities = db.query(FileActivity).order_by(FileActivity.timestamp.desc()).limit(10).all()
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(10).all()
    
    result["recent_activities"] = {
        "logins": [
            {
                "id": login.id,
                "timestamp": login.timestamp,
                "user_id": login.user_id,
                "success": login.success,
                "ip_address": login.ip_address,
            }
            for login in recent_logins
        ],
        "file_activities": [
            {
                "id": activity.id,
                "timestamp": activity.timestamp,
                "user_id": activity.user_id,
                "file_name": activity.file_name,
                "activity_type": activity.activity_type,
            }
            for activity in recent_file_activities
        ],
        "alerts": [
            {
                "id": alert.id,
                "timestamp": alert.timestamp,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "is_resolved": alert.is_resolved,
            }
            for alert in recent_alerts
        ]
    }
    
    return result