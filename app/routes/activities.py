from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..database import get_db
from ..models.user import User
from ..models.activity import LoginActivity, FileActivity
from ..models.alert import Alert

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
from ..services.geoip import geoip_service

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
    is_anomalous: Optional[bool] = None,
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
    
    # Apply anomalous filter
    if is_anomalous is not None:
        query = query.filter(LoginActivity.is_anomalous == is_anomalous)
    
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
    # Add IPinfo information
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
            message=description,
            source_ip=activity_in.ip_address,
            location=geo_data.get("country", "Unknown"),
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
    action: Optional[str] = None,
    is_anomalous: Optional[bool] = None,
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
    
    # Apply action filter
    if action:
        query = query.filter(FileActivity.action == action)
    
    # Apply anomalous filter
    if is_anomalous is not None:
        query = query.filter(FileActivity.is_anomalous == is_anomalous)
    
    # Order and paginate
    activities = query.order_by(FileActivity.timestamp.desc()).offset(skip).limit(limit).all()
    
    return activities


@router.post("/file", status_code=201)
def create_file_activity_simple(
    activity_in: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Create new file activity record with simplified input.
    """
    # Create activity data from input
    activity_data = {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "file_path": activity_in.get("file_path"),
        "action": activity_in.get("action", "VIEW"),
        "ip_address": activity_in.get("ip_address"),
        "timestamp": datetime.utcnow(),
        "is_anomalous": False,
        "details": activity_in.get("details")
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
        "action": db_activity.action,
        "ip_address": db_activity.ip_address,
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
    if activity_in.user_email != current_user.email and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create activities for your own account",
        )
    
    # Create activity object
    activity_data = activity_in.dict()
    activity_data['timestamp'] = datetime.utcnow()
    
    # Check for anomalies
    anomalies = threat_detection.detect_file_anomalies(db, current_user.id, activity_in)
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
            user_id=current_user.id,
            alert_type="file",
            severity=severity,
            message=description,
            source_ip=activity_in.ip_address,
            location="Unknown",
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
    resolved: Optional[bool] = None,
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
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    
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
    alert_data = alert_in.dict()
    alert_data['timestamp'] = datetime.utcnow()
    
    db_alert = Alert(**alert_data)
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
    if update_data.get("resolved") and not update_data.get("resolved_by"):
        update_data["resolved_by"] = current_user.id
        update_data["resolved_at"] = datetime.now()
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# Add dashboard endpoint
@router.get("/dashboard", response_model=Dict[str, Any])
def get_activity_dashboard_data(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get aggregated data for activity dashboard.
    """
    result = {}
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query filters
    login_query = db.query(LoginActivity).filter(LoginActivity.timestamp >= start_date)
    file_query = db.query(FileActivity).filter(FileActivity.timestamp >= start_date)
    alert_query = db.query(Alert).filter(Alert.timestamp >= start_date)
    
    # If not admin, filter by user
    if not current_user.is_admin:
        login_query = login_query.filter(LoginActivity.user_id == current_user.id)
        file_query = file_query.filter(FileActivity.user_id == current_user.id)
        alert_query = alert_query.filter(Alert.user_id == current_user.id)
    
    # Activity counts
    result["total_logins"] = login_query.count()
    result["total_file_activities"] = file_query.count()
    result["total_alerts"] = alert_query.count()
    result["unresolved_alerts"] = alert_query.filter(Alert.resolved == False).count()
    
    # File activity breakdown by type
    file_types = db.query(
        FileActivity.action,
        func.count(FileActivity.id).label("count")
    ).filter(
        FileActivity.timestamp >= start_date
    )
    
    if not current_user.is_admin:
        file_types = file_types.filter(FileActivity.user_id == current_user.id)
    
    result["file_activity_types"] = {
        r[0]: r[1] for r in file_types.group_by(FileActivity.action).all()
    }
    
    # Alert severity breakdown
    alert_severity = db.query(
        Alert.severity,
        func.count(Alert.id).label("count")
    ).filter(
        Alert.timestamp >= start_date
    )
    
    if not current_user.is_admin:
        alert_severity = alert_severity.filter(Alert.user_id == current_user.id)
    
    result["alert_severity"] = {
        r[0]: r[1] for r in alert_severity.group_by(Alert.severity).all()
    }
    
    # Recent activities
    recent_logins = login_query.order_by(LoginActivity.timestamp.desc()).limit(10).all()
    recent_file_activities = file_query.order_by(FileActivity.timestamp.desc()).limit(10).all()
    recent_alerts = alert_query.order_by(Alert.timestamp.desc()).limit(10).all()
    
    result["recent_activities"] = {
        "logins": [
            {
                "id": login.id,
                "timestamp": login.timestamp,
                "user_id": login.user_id,
                "user_email": login.user_email,
                "success": login.success,
                "ip_address": login.ip_address,
                "country": login.country,
                "city": login.city,
                "is_anomalous": login.is_anomalous,
            }
            for login in recent_logins
        ],
        "file_activities": [
            {
                "id": activity.id,
                "timestamp": activity.timestamp,
                "user_id": activity.user_id,
                "user_email": activity.user_email,
                "file_path": activity.file_path,
                "action": activity.action,
                "is_anomalous": activity.is_anomalous,
            }
            for activity in recent_file_activities
        ],
        "alerts": [
            {
                "id": alert.id,
                "timestamp": alert.timestamp,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "resolved": alert.resolved,
                "source_ip": alert.source_ip,
                "location": alert.location,
            }
            for alert in recent_alerts
        ]
    }
    
    return result