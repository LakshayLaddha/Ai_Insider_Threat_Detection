import logging
from typing import Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session

from ..models.activity import Alert
from ..config import settings
from .logger import log_alert

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages the creation and handling of alerts."""
    
    @staticmethod
    def create_alert(
        db: Session,
        user_id: int,
        alert_type: str,
        severity: str,
        description: str,
        login_activity_id: Optional[int] = None,
        file_activity_id: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """
        Create a new alert and save it to database.
        
        Args:
            db: Database session
            user_id: User ID related to the alert
            alert_type: Type of alert (login, file, behavioral)
            severity: Alert severity (low, medium, high, critical)
            description: Alert description
            login_activity_id: Related login activity ID if applicable
            file_activity_id: Related file activity ID if applicable
            additional_data: Additional context data
            
        Returns:
            Created Alert object
        """
        # Create alert
        alert = Alert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            login_activity_id=login_activity_id,
            file_activity_id=file_activity_id,
        )
        
        # Save to database
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Log the alert
        log_data = {}
        if additional_data:
            log_data.update(additional_data)
        if login_activity_id:
            log_data["login_activity_id"] = login_activity_id
        if file_activity_id:
            log_data["file_activity_id"] = file_activity_id
        
        log_alert(
            alert_type=alert_type,
            severity=severity,
            user_id=user_id,
            description=description,
            alert_id=alert.id,
            **log_data
        )
        
        return alert
    
    @staticmethod
    def evaluate_login_anomalies(anomalies: Dict[str, bool]) -> Tuple[bool, str, str]:
        """
        Evaluate login anomalies and determine if an alert should be created.
        
        Args:
            anomalies: Dictionary of detected anomalies
            
        Returns:
            Tuple of (create_alert, severity, description)
        """
        if anomalies.get("is_unusual_location", False) and anomalies.get("is_unusual_time", False):
            # Both unusual location and time - high severity
            return True, "high", "Login from unusual location at unusual time"
        
        if anomalies.get("is_unusual_location", False):
            # Just unusual location - medium severity
            return True, "medium", "Login from unusual location"
        
        if anomalies.get("is_unusual_time", False):
            # Just unusual time - low severity
            return True, "low", "Login at unusual time"
        
        return False, "", ""
    
    @staticmethod
    def evaluate_file_anomalies(anomalies: Dict[str, bool]) -> Tuple[bool, str, str]:
        """
        Evaluate file activity anomalies and determine if an alert should be created.
        
        Args:
            anomalies: Dictionary of detected anomalies
            
        Returns:
            Tuple of (create_alert, severity, description)
        """
        if anomalies.get("is_unusual_volume", False) and anomalies.get("is_sensitive_data", False):
            # High volume of sensitive data - critical
            return True, "critical", "High volume access to sensitive data"
        
        if anomalies.get("is_unusual_volume", False):
            # Just high volume - medium severity
            return True, "medium", "Unusually high volume of file activity"
        
        if anomalies.get("is_sensitive_data", False) and anomalies.get("is_unusual_type", False):
            # Sensitive data of unusual type - high severity
            return True, "high", "Access to unusual sensitive file type"
        
        if anomalies.get("is_sensitive_data", False):
            # Just sensitive data - low severity
            return True, "low", "Access to sensitive data"
        
        return False, "", ""


# Create a singleton instance
alert_manager = AlertManager()