from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class ThreatDetection:
    def detect_login_anomalies(self, db: Session, user_id: int, login_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential anomalous login attempts.
        """
        anomalies = {
            "is_suspicious": False,
            "anomaly_details": [],
        }
        
        # Check for empty or unknown IP address - don't flag as suspicious
        if not login_data.get("ip_address") or login_data.get("ip_address") == "unknown":
            return anomalies
        
        # Example: simple checks for suspicious behavior
        # In a real system, you'd compare against historical data, use ML models, etc.
        if login_data.get("country") and login_data.get("country") not in ["US", "USA", "United States"]:
            anomalies["is_suspicious"] = True
            anomalies["anomaly_details"].append(f"Unusual login country: {login_data.get('country')}")
        
        # Log anomalies
        if anomalies["is_suspicious"]:
            logger.warning(f"Detected login anomalies for user {user_id}: {anomalies['anomaly_details']}")
        
        return anomalies

    def detect_file_anomalies(self, db: Session, user_id: int, file_activity: Any) -> Dict[str, Any]:
        """
        Detect potential anomalous file activities.
        """
        anomalies = {
            "is_suspicious": False,
            "anomaly_details": [],
        }
        
        # Sample logic for file activity anomaly detection
        # In a real system, you'd have more sophisticated checks
        if getattr(file_activity, "action", "").lower() in ["delete", "remove"]:
            # Mark deletions as slightly suspicious
            anomalies["is_suspicious"] = True
            anomalies["anomaly_details"].append("Sensitive file operation detected")
        
        return anomalies

    def should_create_alert(self, anomalies: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Determine if an alert should be created based on detected anomalies.
        """
        if not anomalies.get("is_suspicious", False):
            return False, "", ""
        
        # If suspicious, generate an alert
        details = ", ".join(anomalies.get("anomaly_details", []))
        if not details:
            details = "Suspicious activity detected"
        
        # Determine severity based on number of anomalies
        num_anomalies = len(anomalies.get("anomaly_details", []))
        if num_anomalies >= 3:
            severity = "high"
        elif num_anomalies >= 2:
            severity = "medium"
        else:
            severity = "low"
        
        return True, severity, details


# Create a singleton instance to use throughout the app
threat_detection = ThreatDetection()