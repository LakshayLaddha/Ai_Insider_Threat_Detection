from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import datetime
import random

from ..models.user import User
from .auth import get_current_user

router = APIRouter()

@router.get("/")
def get_dashboard_data(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get mock dashboard data for the current user.
    Uses random generated data for demonstration.
    """
    # Generate mock data
    now = datetime.datetime.now()
    
    # Mock alerts data
    alerts_data = []
    severity_options = ["low", "medium", "high", "critical"]
    alert_types = ["Suspicious Login", "Brute Force Attempt", "File Access", "Configuration Change", "Malware Detected"]
    message_templates = [
        "Unusual login attempt from {0}",
        "Multiple failed login attempts for user {0}",
        "Unauthorized file access attempt on {0}",
        "Critical system file modified: {0}",
        "Suspicious network traffic detected from {0}"
    ]
    
    for i in range(10):
        ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        alert_type = random.choice(alert_types)
        message_template = random.choice(message_templates)
        
        timestamp = now - datetime.timedelta(
            days=random.randint(0, 6), 
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        
        alerts_data.append({
            "id": i + 1,
            "type": alert_type,
            "severity": random.choice(severity_options),
            "message": message_template.format(ip),
            "timestamp": timestamp.isoformat(),
            "source_ip": ip,
            "location": random.choice(["United States", "India", "China", "Russia", "United Kingdom", "Brazil", "Germany"]),
            "resolved": random.choice([True, False])
        })
    
    # Generate activity data for past week
    activity_data = []
    for i in range(7):
        day = now - datetime.timedelta(days=6-i)
        activity_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "successful": random.randint(10, 50),
            "failed": random.randint(0, 15)
        })
    
    # Count critical alerts (for stats)
    critical_alerts = sum(1 for alert in alerts_data if alert["severity"] in ["high", "critical"] and not alert["resolved"])
    
    return {
        "totalAlerts": len(alerts_data),
        "criticalAlerts": critical_alerts,
        "loginAttempts": sum(day["successful"] + day["failed"] for day in activity_data),
        "failedLogins": sum(day["failed"] for day in activity_data),
        "recentThreats": alerts_data,
        "activityData": activity_data
    }