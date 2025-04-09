from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime
import uuid

# Add parent directory to path to import from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from ml_model.isolation_forest import InsiderThreatDetector
from data_preprocessing.feature_engineering import FeatureEngineer
from api_service.schemas import (
    LogEntry, LogResponse, PredictionResponse, 
    ThreatPrediction, FeatureImportance, ModelInfo
)

# Initialize app
app = FastAPI(
    title="Insider Threat Detection API",
    description="AI-powered insider threat detection API for cloud activity logs",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and preprocessor
MODEL_DIR = os.getenv("MODEL_DIR", "../ml_model/trained_models")
LOGS_DIR = os.getenv("LOGS_DIR", "../logs")
detector = None
feature_engineer = None
recent_predictions = []  # In-memory store of recent predictions

# Maximum predictions to store in memory
MAX_RECENT_PREDICTIONS = 100

def get_model():
    """Get or initialize the model."""
    global detector
    if detector is None:
        try:
            detector = InsiderThreatDetector.load_model(MODEL_DIR)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to load model: {str(e)}"
            )
    return detector

def get_feature_engineer():
    """Get or initialize the feature engineer."""
    global feature_engineer
    if feature_engineer is None:
        feature_engineer = FeatureEngineer()
    return feature_engineer

def add_to_recent_predictions(prediction: Dict[str, Any]):
    """Add a prediction to the in-memory store of recent predictions."""
    global recent_predictions
    recent_predictions.append(prediction)
    
    # Keep only the most recent predictions
    if len(recent_predictions) > MAX_RECENT_PREDICTIONS:
        recent_predictions = recent_predictions[-MAX_RECENT_PREDICTIONS:]

@app.get("/", tags=["General"])
async def root():
    """Root endpoint returning API info."""
    return {
        "name": "Insider Threat Detection API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    model_loaded = False
    try:
        # Check if model is loaded
        model = get_model()
        model_loaded = model is not None
    except Exception as e:
        # Log the error but don't raise an exception
        print(f"Warning: Model check failed: {str(e)}")
    
    return {
        "status": "healthy",  # Always return healthy
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info(model: InsiderThreatDetector = Depends(get_model)):
    """Get information about the trained model."""
    return {
        "model_type": model.model_metadata["model_type"],
        "training_date": model.model_metadata["training_date"],
        "contamination": model.model_metadata["contamination"],
        "n_estimators": model.model_metadata["n_estimators"],
        "feature_count": len(model.feature_names),
        "features": model.feature_names
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(
    log_entry: LogEntry,
    model: InsiderThreatDetector = Depends(get_model),
    feature_engineer: FeatureEngineer = Depends(get_feature_engineer)
):
    """
    Make a prediction for a single log entry.
    
    This endpoint takes a cloud log entry, processes it through feature engineering,
    and returns a threat prediction with explanation.
    """
    try:
        # Convert single log to DataFrame for processing
        log_df = pd.DataFrame([log_entry.dict()])
        
        # Apply feature engineering
        features_df = feature_engineer.transform(log_df)
        
        # Check for missing features
        required_features = set(model.feature_names)
        missing_features = required_features - set(features_df.columns)
        
        if missing_features:
            # Add missing features with default values
            for feature in missing_features:
                features_df[feature] = 0
        
        # Ensure features are in the right order
        features_df = features_df[model.feature_names]
        
        # Make prediction
        anomaly_score, is_anomaly = model.predict(features_df)
        
        # Get explanations
        explanations = model.explain_predictions(features_df, top_n=3)
        
        # Create response
        prediction = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_id": log_entry.user_id,
            "ip_address": log_entry.ip_address,
            "action": log_entry.action,
            "resource": log_entry.resource,
            "threat_score": float(anomaly_score[0]),
            "is_threat": bool(is_anomaly[0]),
            "top_features": [
                {
                    "feature_name": feature["feature_name"],
                    "feature_value": feature["feature_value"],
                    "importance": abs(feature["z_score"]),
                    "is_high": feature["is_high"]
                } for feature in explanations[0]["top_features"]
            ],
            "reasons": generate_explanation_text(explanations[0], features_df, is_anomaly[0])
        }
        
        # Add to recent predictions
        add_to_recent_predictions(prediction)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict/batch", response_model=List[PredictionResponse], tags=["Predictions"])
async def predict_batch(
    log_entries: List[LogEntry],
    model: InsiderThreatDetector = Depends(get_model),
    feature_engineer: FeatureEngineer = Depends(get_feature_engineer)
):
    """Make predictions for multiple log entries."""
    try:
        # Convert logs to DataFrame
        logs_df = pd.DataFrame([log.dict() for log in log_entries])
        
        # Apply feature engineering
        features_df = feature_engineer.transform(logs_df)
        
        # Check for missing features
        required_features = set(model.feature_names)
        missing_features = required_features - set(features_df.columns)
        
        if missing_features:
            # Add missing features with default values
            for feature in missing_features:
                features_df[feature] = 0
        
        # Ensure features are in the right order
        features_df = features_df[model.feature_names]
        
        # Make predictions
        anomaly_scores, is_anomaly = model.predict(features_df)
        
        # Get explanations
        explanations = model.explain_predictions(features_df)
        
        # Create response
        predictions = []
        for i, log_entry in enumerate(log_entries):
            prediction = {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "user_id": log_entry.user_id,
                "ip_address": log_entry.ip_address,
                "action": log_entry.action,
                "resource": log_entry.resource,
                "threat_score": float(anomaly_scores[i]),
                "is_threat": bool(is_anomaly[i]),
                "top_features": [
                    {
                        "feature_name": feature["feature_name"],
                        "feature_value": feature["feature_value"],
                        "importance": abs(feature["z_score"]),
                        "is_high": feature["is_high"]
                    } for feature in explanations[i]["top_features"]
                ],
                "reasons": generate_explanation_text(explanations[i], features_df.iloc[[i]], is_anomaly[i])
            }
            predictions.append(prediction)
            
            # Add to recent predictions
            add_to_recent_predictions(prediction)
        
        return predictions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )

@app.get("/predictions/recent", response_model=List[PredictionResponse], tags=["History"])
async def get_recent_predictions(
    limit: int = Query(10, description="Maximum number of predictions to return")
):
    """Get recent threat predictions stored in memory."""
    global recent_predictions
    
    # Return the most recent predictions
    return recent_predictions[-limit:] if recent_predictions else []

@app.get("/analytics/threats", tags=["Analytics"])
async def get_threat_analytics():
    """Get analytics on detected threats."""
    global recent_predictions
    
    if not recent_predictions:
        return {
            "total_logs_analyzed": 0,
            "threat_count": 0,
            "threat_percentage": 0,
            "top_users": [],
            "top_ips": []
        }
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(recent_predictions)
    
    # Calculate threat statistics
    total_logs = len(df)
    threats = df[df["is_threat"] == True]
    threat_count = len(threats)
    threat_percentage = (threat_count / total_logs) * 100 if total_logs > 0 else 0
    
    # Get top users with threats
    top_users = []
    if not threats.empty and "user_id" in threats.columns:
        user_counts = threats["user_id"].value_counts().head(5)
        top_users = [
            {"user_id": user, "threat_count": int(count)}
            for user, count in user_counts.items()
        ]
    
    # Get top IPs with threats
    top_ips = []
    if not threats.empty and "ip_address" in threats.columns:
        ip_counts = threats["ip_address"].value_counts().head(5)
        top_ips = [
            {"ip_address": ip, "threat_count": int(count)}
            for ip, count in ip_counts.items()
        ]
    
    return {
        "total_logs_analyzed": total_logs,
        "threat_count": threat_count,
        "threat_percentage": threat_percentage,
        "top_users": top_users,
        "top_ips": top_ips
    }

def generate_explanation_text(explanation: Dict, features: pd.DataFrame, is_threat: bool) -> List[str]:
    """Generate human-readable explanations for a prediction."""
    if not is_threat:
        return ["Normal activity detected"]
    
    reasons = []
    
    for feature in explanation["top_features"]:
        feature_name = feature["feature_name"]
        is_high = feature["is_high"]
        value = feature["feature_value"]
        
        if feature_name == "is_unusual_hour" and value > 0:
            reasons.append("Access at unusual hours")
        elif feature_name == "is_unusual_ip" and value > 0:
            reasons.append("Access from unusual IP address")
        elif feature_name == "is_large_data_transfer" and value > 0:
            reasons.append("Unusually large data transfer")
        elif feature_name == "is_weekend" and value > 0:
            reasons.append("Access during weekend")
        elif feature_name == "is_night" and value > 0:
            reasons.append("Access during night hours")
        elif feature_name == "is_high_access_frequency" and value > 0:
            reasons.append("Unusually high access frequency")
        elif feature_name == "is_sensitive_action" and value > 0:
            reasons.append("Performed sensitive action")
        elif feature_name == "is_unusual_action" and value > 0:
            reasons.append("Performed unusual action for this user")
        elif feature_name == "is_unusual_country" and value > 0:
            reasons.append("Access from unusual country")
        elif feature_name == "is_impossible_travel" and value > 0:
            reasons.append("Impossible travel pattern detected")
        elif "zscore" in feature_name and is_high:
            reasons.append(f"Unusual value for {feature_name.replace('_zscore', '')}")
    
    if not reasons:
        # Generic message if no specific reasons are found
        reasons.append("Multiple unusual patterns detected")
    
    return reasons

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)