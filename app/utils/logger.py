import logging
import json
from typing import Any, Dict, Optional, Union
from datetime import datetime

logger = logging.getLogger("insider_sentinel")


def log_activity(
    activity_type: str,
    user_id: Optional[int],
    data: Dict[str, Any],
    level: str = "info",
    is_suspicious: bool = False,
) -> None:
    """
    Log an activity with structured data.
    
    Args:
        activity_type: Type of activity (login, file_access, etc.)
        user_id: ID of the user performing the activity
        data: Additional data about the activity
        level: Log level (info, warning, error)
        is_suspicious: Whether the activity is suspicious
    """
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "activity_type": activity_type,
        "user_id": user_id,
        "is_suspicious": is_suspicious,
        **data
    }
    
    log_message = json.dumps(log_data)
    
    if level.lower() == "warning":
        logger.warning(log_message)
    elif level.lower() == "error":
        logger.error(log_message)
    else:
        logger.info(log_message)


def log_login(user_id: int, success: bool, ip_address: str, user_agent: Optional[str] = None, **kwargs) -> None:
    """
    Log a login attempt.
    
    Args:
        user_id: User ID
        success: Whether login was successful
        ip_address: Client IP address
        user_agent: Client user agent
        **kwargs: Additional data
    """
    level = "info" if success else "warning"
    log_activity(
        activity_type="login",
        user_id=user_id,
        data={
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            **kwargs
        },
        level=level
    )


def log_file_access(
    user_id: int,
    action: str,
    file_name: str,
    file_path: Optional[str] = None,
    file_size: Optional[int] = None,
    is_suspicious: bool = False,
    **kwargs
) -> None:
    """
    Log a file access.
    
    Args:
        user_id: User ID
        action: Action performed (download, upload, view, delete)
        file_name: Name of the file
        file_path: Path to the file
        file_size: Size of the file in bytes
        is_suspicious: Whether the activity is suspicious
        **kwargs: Additional data
    """
    level = "warning" if is_suspicious else "info"
    log_activity(
        activity_type="file_access",
        user_id=user_id,
        data={
            "action": action,
            "file_name": file_name,
            "file_path": file_path,
            "file_size": file_size,
            **kwargs
        },
        level=level,
        is_suspicious=is_suspicious
    )


def log_alert(
    alert_type: str, 
    severity: str, 
    user_id: int, 
    description: str,
    **kwargs
) -> None:
    """
    Log an alert.
    
    Args:
        alert_type: Type of alert (login, file, behavioral)
        severity: Alert severity (low, medium, high, critical)
        user_id: User ID related to the alert
        description: Alert description
        **kwargs: Additional data
    """
    # Map severity to log level
    level_map = {
        "low": "info",
        "medium": "info",
        "high": "warning",
        "critical": "error"
    }
    level = level_map.get(severity.lower(), "warning")
    
    log_activity(
        activity_type="alert",
        user_id=user_id,
        data={
            "alert_type": alert_type,
            "severity": severity,
            "description": description,
            **kwargs
        },
        level=level,
        is_suspicious=True
    )