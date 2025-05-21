from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import datetime

from ....database import get_db
from ....models.user import User
from ....models.activity import LoginActivity
from ....models.alert import Alert
from ...deps import get_current_user

router = APIRouter()

@router.get("/")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard data for the current user.
    """
    # Calculate date range for queries
    now = datetime.datetime.now()
    last_week = now - datetime.timedelta(days=7)
    
    # Get total alerts
    total_alerts = db.query(Alert).count()
    
    # Get critical alerts
    critical_alerts = db.query(Alert).filter(
        Alert.severity.in_(["high", "critical"]),
        Alert.resolved == False
    ).count()
    
    # Get login attempts for the past week
    login_attempts = db.query(LoginActivity).filter(
        LoginActivity.timestamp >= last_week
    ).count()
    
    # Get failed logins for the past week
    failed_logins = db.query(LoginActivity).filter(
        LoginActivity.timestamp >= last_week,
        LoginActivity.success == False
    ).count()
    
    # Get recent threats (alerts)
    recent_threats = db.query(Alert).order_by(
        Alert.timestamp.desc()
    ).limit(10).all()
    
    # Format alerts for frontend
    alerts_data = []
    for alert in recent_threats:
        alerts_data.append({
            "id": alert.id,
            "type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "source_ip": alert.source_ip,
            "location": alert.location,
            "resolved": alert.resolved
        })
    
    # Get activity data for the past week (daily counts)
    activity_data = []
    for i in range(7):
        day = now - datetime.timedelta(days=i)
        day_start = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
        
        success_count = db.query(LoginActivity).filter(
            LoginActivity.timestamp >= day_start,
            LoginActivity.timestamp <= day_end,
            LoginActivity.success == True
        ).count()
        
        failed_count = db.query(LoginActivity).filter(
            LoginActivity.timestamp >= day_start,
            LoginActivity.timestamp <= day_end,
            LoginActivity.success == False
        ).count()
        
        activity_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "successful": success_count,
            "failed": failed_count
        })
    
    # Reverse to get chronological order
    activity_data.reverse()
    
    return {
        "totalAlerts": total_alerts,
        "criticalAlerts": critical_alerts,
        "loginAttempts": login_attempts,
        "failedLogins": failed_logins,
        "recentThreats": alerts_data,
        "activityData": activity_data
    }