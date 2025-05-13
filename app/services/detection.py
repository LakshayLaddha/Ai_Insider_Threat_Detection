import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.activity import FileActivity, LoginActivity
from ..models.user import User
from ..config import settings

logger = logging.getLogger(__name__)


class ThreatDetectionService:
    """Service for detecting suspicious activities."""
    
    def detect_file_anomalies(
        self, db: Session, user_id: int, activity: FileActivity
    ) -> Dict[str, bool]:
        """
        Detect anomalies in file activities.
        
        Args:
            db: Database session.
            user_id: User ID.
            activity: File activity to check.
            
        Returns:
            Dictionary with anomaly flags.
        """
        result = {
            "is_unusual_volume": False,
            "is_unusual_type": False,
            "is_sensitive_data": False,
            "is_suspicious": False
        }
        
        # 1. Check for unusual volume (many files in short period)
        recent_count = db.query(FileActivity).filter(
            FileActivity.user_id == user_id,
            FileActivity.timestamp >= datetime.now() - timedelta(hours=1)
        ).count()
        
        if recent_count > settings.MAX_FILE_DOWNLOADS:
            result["is_unusual_volume"] = True
            result["is_suspicious"] = True
            logger.warning(f"Unusual file activity volume detected for user {user_id}: {recent_count} activities in the last hour")
        
        # 2. Check for sensitive data based on file type or name
        sensitive_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv']
        sensitive_keywords = ['confidential', 'secret', 'sensitive', 'private', 'personal']
        
        if activity.file_name:
            # Check file extension
            if any(activity.file_name.lower().endswith(ext) for ext in sensitive_extensions):
                result["is_sensitive_data"] = True
            
            # Check for sensitive keywords in filename
            if any(keyword in activity.file_name.lower() for keyword in sensitive_keywords):
                result["is_sensitive_data"] = True
                result["is_suspicious"] = True
        
        # 3. Check if file type is unusual for this user
        if activity.file_type:
            # Get user's common file types
            common_types = db.query(
                FileActivity.file_type, 
                func.count(FileActivity.id).label('count')
            ).filter(
                FileActivity.user_id == user_id
            ).group_by(FileActivity.file_type).order_by(func.count(FileActivity.id).desc()).limit(5).all()
            
            common_types_list = [t[0] for t in common_types if t[0]]
            
            if common_types_list and activity.file_type not in common_types_list:
                result["is_unusual_type"] = True
                # Only mark as suspicious if sensitive and unusual type
                if result["is_sensitive_data"]:
                    result["is_suspicious"] = True
        
        return result
    
    def detect_login_anomalies(
        self, db: Session, user_id: int, login: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Detect anomalies in login activities.
        
        Args:
            db: Database session.
            user_id: User ID.
            login: Login data including IP, timestamp, etc.
            
        Returns:
            Dictionary with anomaly flags.
        """
        result = {
            "is_unusual_location": False,
            "is_unusual_time": False,
            "is_suspicious": False
        }
        
        # 1. Check for unusual login time
        current_hour = datetime.now().hour
        if (current_hour >= settings.UNUSUAL_TIME_START or 
            current_hour <= settings.UNUSUAL_TIME_END):
            result["is_unusual_time"] = True
        
        # 2. Check for unusual login location
        if 'ip_address' in login:
            # Get user's common login locations
            common_locations = db.query(
                LoginActivity.country,
                func.count(LoginActivity.id).label('count')
            ).filter(
                LoginActivity.user_id == user_id,
                LoginActivity.country.isnot(None)
            ).group_by(LoginActivity.country).order_by(func.count(LoginActivity.id).desc()).all()
            
            common_countries = [loc[0] for loc in common_locations if loc[0]]
            
            # If we have location data for this login
            if login.get('country') and common_countries:
                if login['country'] not in common_countries:
                    result["is_unusual_location"] = True
                    # Unusual location is always suspicious
                    result["is_suspicious"] = True
        
        # 3. Check for concurrent logins from different locations
        active_logins = db.query(LoginActivity).filter(
            LoginActivity.user_id == user_id,
            LoginActivity.timestamp >= datetime.now() - timedelta(hours=1),
            LoginActivity.logout_time.is_(None)  # Still logged in
        ).all()
        
        locations = set()
        for active in active_logins:
            if active.country:
                locations.add(active.country)
        
        # If logged in from multiple countries simultaneously
        if len(locations) > 1:
            result["is_unusual_location"] = True
            result["is_suspicious"] = True
            logger.warning(f"Concurrent logins from different countries detected for user {user_id}: {locations}")
        
        return result
    
    def should_create_alert(self, anomalies: Dict[str, bool]) -> Tuple[bool, str, str]:
        """
        Determine if an alert should be created based on detected anomalies.
        
        Args:
            anomalies: Dictionary of detected anomalies.
            
        Returns:
            Tuple of (create_alert, severity, description)
        """
        if anomalies.get("is_suspicious", False):
            severity = "high"
            reasons = []
            
            if anomalies.get("is_unusual_location", False):
                reasons.append("unusual login location")
            if anomalies.get("is_unusual_time", False):
                reasons.append("unusual login time")
            if anomalies.get("is_unusual_volume", False):
                reasons.append("high volume of file activities")
            if anomalies.get("is_sensitive_data", False):
                reasons.append("access to sensitive data")
            if anomalies.get("is_unusual_type", False):
                reasons.append("unusual file type")
            
            description = "Suspicious activity detected: " + ", ".join(reasons)
            return True, severity, description
        
        elif (anomalies.get("is_unusual_location", False) or
              anomalies.get("is_unusual_time", False) or
              anomalies.get("is_unusual_volume", False)):
            return True, "medium", "Unusual activity detected"
        
        return False, "low", "Normal activity"


# Singleton instance
threat_detection = ThreatDetectionService()