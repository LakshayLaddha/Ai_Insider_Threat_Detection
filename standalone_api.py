import os
import pickle
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Insider Threat Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Saved threats (in-memory database)
saved_threats = []

# Try to load the model from the container
model = None
try:
    # Check if exported model exists
    if os.path.exists("isolation_forest_model.pkl"):
        with open("isolation_forest_model.pkl", "rb") as f:
            model = pickle.load(f)
        print("Loaded model from local file")
except Exception as e:
    print(f"Could not load model: {e}")

# Model features
MODEL_FEATURES = [
    "hour", "day_of_week", 
    "user_id_admin", "user_id_system", "user_id_lakshay", "user_id_other",
    "action_read", "action_write", "action_login", "action_download", "action_delete", "action_modify", "action_execute",
    "resource_financial", "resource_customer", "resource_employee", "resource_source", "resource_infrastructure", "resource_security",
    "data_size", "is_suspicious_ip"
]

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/model/info")
def model_info():
    return {
        "model_type": "IsolationForest",
        "training_date": "2025-04-09T00:48:03.196794",
        "contamination": 0.2,
        "n_estimators": 100,
        "feature_count": 21,
        "features": MODEL_FEATURES
    }

def extract_features(log_entry):
    """Extract features from a log entry"""
    # Ensure log_entry has a date
    if "date" not in log_entry and "timestamp" in log_entry:
        try:
            timestamp = datetime.fromisoformat(log_entry["timestamp"].replace("Z", "+00:00"))
            log_entry["date"] = timestamp.strftime("%Y-%m-%d")
        except Exception:
            log_entry["date"] = datetime.now().strftime("%Y-%m-%d")
            
    # Initialize features
    features = {}
    
    # Time features
    try:
        if "timestamp" in log_entry:
            timestamp = datetime.fromisoformat(log_entry["timestamp"].replace("Z", "+00:00"))
            features["hour"] = timestamp.hour
            features["day_of_week"] = timestamp.weekday()  # 0-6, Monday is 0
        else:
            features["hour"] = log_entry.get("hour", datetime.now().hour)
            features["day_of_week"] = log_entry.get("day_of_week", datetime.now().weekday())
    except Exception:
        features["hour"] = log_entry.get("hour", datetime.now().hour)
        features["day_of_week"] = log_entry.get("day_of_week", datetime.now().weekday())
    
    # User features
    user_id = log_entry.get("user_id", "").lower()
    features["user_id_admin"] = 1 if "admin" in user_id else 0
    features["user_id_system"] = 1 if "system" in user_id else 0
    features["user_id_lakshay"] = 1 if "lakshay" in user_id else 0
    features["user_id_other"] = 1 if not any(x in user_id for x in ["admin", "system", "lakshay"]) else 0
    
    # Action features
    action = log_entry.get("action", "").upper()
    features["action_read"] = 1 if action == "READ" else 0
    features["action_write"] = 1 if action == "WRITE" else 0
    features["action_login"] = 1 if action == "LOGIN" else 0
    features["action_download"] = 1 if action == "DOWNLOAD" else 0
    features["action_delete"] = 1 if action == "DELETE" else 0
    features["action_modify"] = 1 if action == "MODIFY" else 0
    features["action_execute"] = 1 if action == "EXECUTE" else 0
    
    # Resource features
    resource = log_entry.get("resource", "").upper()
    features["resource_financial"] = 1 if "FINANCIAL" in resource else 0
    features["resource_customer"] = 1 if "CUSTOMER" in resource else 0
    features["resource_employee"] = 1 if "EMPLOYEE" in resource else 0
    features["resource_source"] = 1 if "SOURCE" in resource else 0
    features["resource_infrastructure"] = 1 if "INFRASTRUCTURE" in resource else 0
    features["resource_security"] = 1 if "SECURITY" in resource else 0
    
    # Other features
    features["data_size"] = log_entry.get("data_size", 0)
    
    # Suspicious IP detection
    ip_address = log_entry.get("ip_address", "")
    suspicious_ips = ["45.227.253.77", "103.152.36.49", "185.176.27.132"]
    features["is_suspicious_ip"] = 1 if ip_address in suspicious_ips else 0
    
    return features

@app.post("/predict")
def predict(log_entry: dict):
    """Make a prediction on a log entry"""
    try:
        # Extract features
        features = extract_features(log_entry)
        
        # Create DataFrame with only the model features
        df = pd.DataFrame([features])
        
        # Make prediction
        if model is not None:
            # Get raw anomaly scores (negative = more anomalous)
            raw_scores = model.score_samples(df)
            
            # Convert to a threat score (0 to 1, higher = more suspicious)
            # -8 is a very anomalous score, 0 is normal
            min_score = -8
            threat_score = np.clip(1 - (raw_scores - min_score) / (-min_score), 0, 1)[0]
        else:
            # Fallback scoring logic if model is not available
            threat_score = 0.0
            
            # Night-time activity
            if features["hour"] < 6:
                threat_score += 0.3
                
            # Admin/system user with sensitive actions
            if (features["user_id_admin"] or features["user_id_system"]) and any([
                features["action_download"], features["action_delete"], 
                features["action_modify"], features["action_execute"]
            ]):
                threat_score += 0.2
                
            # Sensitive resources
            if any([features["resource_source"], features["resource_infrastructure"], 
                   features["resource_security"]]):
                threat_score += 0.2
                
            # Suspicious IP
            if features["is_suspicious_ip"]:
                threat_score += 0.3
                
            # Large data transfers
            if features["data_size"] > 1000000:
                threat_score += 0.1
                
            threat_score = min(threat_score, 0.99)
        
        # Determine if it's a threat
        is_threat = bool(threat_score > 0.7)
        
        # Store prediction for later retrieval
        prediction_id = len(saved_threats) + 1
        
        # Create threat record
        threat_record = {
            "id": str(prediction_id),
            "timestamp": log_entry.get("timestamp", datetime.now().isoformat()),
            "user_id": log_entry.get("user_id", "unknown"),
            "action": log_entry.get("action", "UNKNOWN"),
            "resource": log_entry.get("resource", "UNKNOWN"),
            "ip_address": log_entry.get("ip_address", "0.0.0.0"),
            "data_size": log_entry.get("data_size", 0),
            "threat_score": float(threat_score),
            "is_threat": is_threat,
            "status": "NEW",
            "features": features,
            "details": {
                "anomalous_features": []
            }
        }
        
        # Add anomalous features
        anomalies = []
        if features["hour"] < 6:
            anomalies.append({"feature": "Time of Day", "value": features["hour"], "significance": 0.9})
        if features["is_suspicious_ip"]:
            anomalies.append({"feature": "IP Address", "value": log_entry.get("ip_address"), "significance": 0.85})
        if features["data_size"] > 1000000:
            anomalies.append({"feature": "Data Size", "value": f"{features['data_size']/1024:.0f} KB", "significance": 0.75})
        if any([features["resource_source"], features["resource_infrastructure"], features["resource_security"]]):
            anomalies.append({"feature": "Resource Type", "value": log_entry.get("resource"), "significance": 0.8})
        if any([features["action_download"], features["action_delete"], features["action_modify"], features["action_execute"]]):
            anomalies.append({"feature": "Action Type", "value": log_entry.get("action"), "significance": 0.7})
        
        threat_record["details"]["anomalous_features"] = anomalies
        
        # Save if it's a threat
        if is_threat:
            saved_threats.append(threat_record)
        
        # Return prediction
        result = {
            "is_threat": is_threat,
            "threat_score": float(threat_score),
            "prediction_time": datetime.now().isoformat(),
            "features_used": list(features.keys())
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/threats")
def get_threats():
    """Get all saved threats"""
    return {"threats": saved_threats}

@app.get("/generate-demo-data")
def generate_demo_data(count: int = 10):
    """Generate demo threat data"""
    now = datetime.now()
    demo_threats = []
    
    for i in range(count):
        # Alternate between threat and normal activity
        is_threat = i % 2 == 0
        
        # Time features
        if is_threat:
            hour = random.randint(0, 5)  # Night hours (suspicious)
            timestamp = now - timedelta(hours=random.randint(1, 48))
            timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        else:
            hour = random.randint(9, 17)  # Business hours (normal)
            timestamp = now - timedelta(hours=random.randint(1, 48))
            timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        
        # User
        if is_threat:
            user_id = random.choice(["admin", "system"])
        else:
            user_id = random.choice(["user_1", "user_2", "user_3", "lakshay.laddha"])
        
        # Action
        if is_threat:
            action = random.choice(["DOWNLOAD", "DELETE", "MODIFY", "EXECUTE"])
        else:
            action = random.choice(["READ", "WRITE", "LOGIN"])
        
        # Resource
        if is_threat:
            resource = random.choice(["SOURCE_CODE", "INFRASTRUCTURE_CONFIG", "SECURITY_KEYS"])
        else:
            resource = random.choice(["FINANCIAL_DATA", "CUSTOMER_DATABASE", "EMPLOYEE_RECORDS"])
        
        # IP
        if is_threat:
            ip_address = random.choice(["45.227.253.77", "103.152.36.49", "185.176.27.132"])
        else:
            ip_address = random.choice(["192.168.1.105", "10.0.0.123"])
        
        # Data size
        if is_threat:
            data_size = random.randint(500000, 5000000)
        else:
            data_size = random.randint(1000, 100000)
        
        # Create log entry
        log = {
            "user_id": user_id,
            "action": action,
            "timestamp": timestamp.isoformat(),
            "resource": resource,
            "ip_address": ip_address,
            "data_size": data_size
        }
        
        # Make prediction
        result = predict(log)
        
        # Add generated threat to our list to return
        if result["is_threat"]:
            demo_threats.append(log)
    
    return {"demo_threats": demo_threats}

if __name__ == "__main__":
    import random
    port = 8080
    print(f"Starting standalone API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)