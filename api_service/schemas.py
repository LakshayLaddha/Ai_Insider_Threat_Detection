from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class LogEntry(BaseModel):
    """Schema for incoming log entries."""
    user_id: str = Field(..., description="User identifier")
    action: str = Field(..., description="Action performed (e.g., LOGIN, READ, WRITE)")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the action occurred")
    resource: str = Field(..., description="Resource that was accessed")
    ip_address: str = Field(..., description="IP address of the user")
    data_size: int = Field(0, description="Size of data transferred in bytes")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_12",
                "action": "DOWNLOAD",
                "timestamp": "2025-04-08T03:24:53",
                "resource": "S3_BUCKET",
                "ip_address": "192.168.1.105",
                "data_size": 524288
            }
        }

class LogResponse(BaseModel):
    """Schema for log entry response."""
    id: str
    user_id: str
    action: str
    timestamp: datetime
    resource: str
    ip_address: str
    data_size: int
    
    class Config:
        schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
                "user_id": "user_12",
                "action": "DOWNLOAD",
                "timestamp": "2025-04-08T03:24:53",
                "resource": "S3_BUCKET", 
                "ip_address": "192.168.1.105",
                "data_size": 524288
            }
        }

class FeatureImportance(BaseModel):
    """Schema for feature importance in predictions."""
    feature_name: str = Field(..., description="Name of the feature")
    feature_value: float = Field(..., description="Value of the feature")
    importance: float = Field(..., description="Importance score of the feature")
    is_high: bool = Field(..., description="Whether the value is higher than normal")

class ThreatPrediction(BaseModel):
    """Schema for threat prediction results."""
    threat_score: float = Field(..., description="Anomaly score (0-1)")
    is_threat: bool = Field(..., description="Whether the activity is flagged as a threat")
    top_features: List[FeatureImportance] = Field([], description="Top contributing features")
    reasons: List[str] = Field([], description="Human-readable explanation of the threat")

class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    log_id: str = Field(..., description="Unique identifier for this prediction")
    timestamp: datetime = Field(..., description="When the prediction was made")
    user_id: str = Field(..., description="User identifier")
    ip_address: str = Field(..., description="IP address")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource accessed")
    threat_score: float = Field(..., description="Anomaly score (0-1)")
    is_threat: bool = Field(..., description="Whether activity is flagged as a threat")
    top_features: List[FeatureImportance] = Field([], description="Top contributing features")
    reasons: List[str] = Field([], description="Human-readable explanations")
    
    class Config:
        schema_extra = {
            "example": {
                "log_id": "b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7",
                "timestamp": "2025-04-08T15:30:45",
                "user_id": "user_12",
                "ip_address": "192.168.1.105",
                "action": "DOWNLOAD",
                "resource": "S3_BUCKET",
                "threat_score": 0.89,
                "is_threat": True,
                "top_features": [
                    {
                        "feature_name": "is_unusual_hour",
                        "feature_value": 1.0,
                        "importance": 0.78,
                        "is_high": True
                    },
                    {
                        "feature_name": "data_size_zscore",
                        "feature_value": 2.3,
                        "importance": 0.65,
                        "is_high": True
                    }
                ],
                "reasons": [
                    "Access at unusual hours",
                    "Unusually large data transfer"
                ]
            }
        }

class ModelInfo(BaseModel):
    """Schema for model information."""
    model_type: str
    training_date: str
    contamination: float
    n_estimators: int
    feature_count: int
    features: List[str]