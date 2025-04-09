import subprocess
import time
import os

# Create the router file with our working prediction endpoint
router_code = """
from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime
import traceback
import logging
import os
import json
import numpy as np
import pickle

# Create router
router = APIRouter()

# Load the model
MODEL_PATH = "/app/ml_model/trained_models"
model = None

try:
    if os.path.exists(MODEL_PATH):
        model_files = [f for f in os.listdir(MODEL_PATH) if f.endswith('.pkl')]
        if model_files:
            model_file = os.path.join(MODEL_PATH, model_files[0])
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
                print(f"Model loaded from {MODEL_PATH}")
        else:
            print(f"No model files found in {MODEL_PATH}")
    else:
        print(f"Model directory not found: {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")

# Working feature extraction function
def extract_features(log_entry):
    # Make sure date field exists
    if 'date' not in log_entry and 'timestamp' in log_entry:
        try:
            timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
            log_entry['date'] = timestamp.strftime('%Y-%m-%d')
        except Exception:
            log_entry['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize features
    features = {}
    
    # Time features
    try:
        if 'timestamp' in log_entry:
            timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
            features['hour'] = timestamp.hour
            features['day_of_week'] = timestamp.weekday()  # 0-6, Monday is 0
        else:
            features['hour'] = log_entry.get('hour', datetime.now().hour)
            features['day_of_week'] = log_entry.get('day_of_week', datetime.now().weekday())
    except Exception:
        features['hour'] = log_entry.get('hour', datetime.now().hour)
        features['day_of_week'] = log_entry.get('day_of_week', datetime.now().weekday())
    
    # User ID features (one-hot encoded)
    user_id = log_entry.get('user_id', '').lower()
    features['user_id_admin'] = 1 if 'admin' in user_id else 0
    features['user_id_system'] = 1 if 'system' in user_id else 0
    features['user_id_lakshay'] = 1 if 'lakshay' in user_id else 0
    features['user_id_other'] = 1 if not any(x in user_id for x in ['admin', 'system', 'lakshay']) else 0
    
    # Action features (one-hot encoded)
    action = log_entry.get('action', '').upper()
    features['action_read'] = 1 if action == 'READ' else 0
    features['action_write'] = 1 if action == 'WRITE' else 0
    features['action_login'] = 1 if action == 'LOGIN' else 0
    features['action_download'] = 1 if action == 'DOWNLOAD' else 0
    features['action_delete'] = 1 if action == 'DELETE' else 0
    features['action_modify'] = 1 if action == 'MODIFY' else 0
    features['action_execute'] = 1 if action == 'EXECUTE' else 0
    
    # Resource features (one-hot encoded)
    resource = log_entry.get('resource', '').upper()
    features['resource_financial'] = 1 if 'FINANCIAL' in resource else 0
    features['resource_customer'] = 1 if 'CUSTOMER' in resource else 0
    features['resource_employee'] = 1 if 'EMPLOYEE' in resource else 0
    features['resource_source'] = 1 if 'SOURCE' in resource else 0
    features['resource_infrastructure'] = 1 if 'INFRASTRUCTURE' in resource else 0
    features['resource_security'] = 1 if 'SECURITY' in resource else 0
    
    # Other features
    features['data_size'] = log_entry.get('data_size', 0)
    
    # Suspicious IP detection
    ip_address = log_entry.get('ip_address', '')
    suspicious_ips = ['45.227.253.77', '103.152.36.49', '185.176.27.132']
    features['is_suspicious_ip'] = 1 if ip_address in suspicious_ips else 0
    
    # Return the Series
    return features

@router.post("/predict")
async def predict(log_entry: dict):
    try:
        print("Starting feature engineering process...")
        
        # Extract features
        features = extract_features(log_entry)
        
        # Create DataFrame with features
        df = pd.DataFrame([features])
        
        # Make prediction
        if model is not None:
            # Get raw anomaly scores (negative = more anomalous)
            raw_scores = model.score_samples(df)
            
            # Convert to a threat score (0 to 1, higher = more suspicious)
            # -8 is a very anomalous score, 0 is normal
            min_score = -8
            threat_score = np.clip(1 - (raw_scores - min_score) / (-min_score), 0, 1)[0]
            is_threat = bool(threat_score > 0.7)
        else:
            # Fallback logic if model is not available
            threat_score = 0.0
            
            # Check for suspicious patterns
            if features['hour'] < 6:  # Night-time activity
                threat_score += 0.3
            
            if (features['user_id_admin'] or features['user_id_system']) and any([
                features['action_download'], features['action_delete'], 
                features['action_modify'], features['action_execute']
            ]):
                threat_score += 0.2
            
            if any([features['resource_source'], features['resource_infrastructure'], 
                   features['resource_security']]):
                threat_score += 0.2
            
            if features['is_suspicious_ip']:
                threat_score += 0.3
            
            if features['data_size'] > 1000000:  # Large data transfer
                threat_score += 0.1
            
            # Cap at 1.0
            threat_score = min(threat_score, 0.99)
            is_threat = bool(threat_score > 0.7)
        
        # Prepare result
        result = {
            "is_threat": is_threat,
            "threat_score": float(threat_score),
            "prediction_time": datetime.now().isoformat(),
            "features_used": list(features.keys())
        }
        
        # Try to store the prediction if such functionality exists
        try:
            from ml_model.database import store_prediction
            store_prediction(log_entry, is_threat, threat_score)
        except Exception as e:
            logging.warning(f"Could not store prediction: {e}")
        
        return result
    
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}\\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
"""

# Create a file that updates the main.py
main_updater = """
import os
import sys
import re
import importlib
import traceback

# Add current directory to path
sys.path.append('/app')
print("Current directory files:", os.listdir('/app'))

def update_main():
    # Path to main.py
    main_path = os.path.join('/app', 'main.py')
    
    if not os.path.exists(main_path):
        print(f"Main app file not found at: {main_path}")
        # Try to look for it elsewhere
        for root, dirs, files in os.walk('/app'):
            if 'main.py' in files:
                main_path = os.path.join(root, 'main.py')
                print(f"Found main.py at: {main_path}")
                break
    
    if not os.path.exists(main_path):
        print("Could not find main.py anywhere in the app directory")
        return False
    
    # Create a backup
    with open(main_path, 'r') as f:
        original_content = f.read()
    
    # Save backup
    backup_path = main_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(original_content)
    print(f"Created backup at {backup_path}")
    
    # Check if 'fixed_router' is already imported
    if 'from fixed_router import router' in original_content:
        print("Fixed router already imported, skipping update")
        return True
    
    # Find import statements to add our import after
    import_loc = -1
    app_loc = -1
    include_router_loc = -1
    
    lines = original_content.split('\\n')
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_loc = i
        if 'FastAPI(' in line:
            app_loc = i
        if '.include_router(' in line:
            include_router_loc = i
    
    if import_loc >= 0:
        # Add our import after the last import
        lines.insert(import_loc + 1, 'from fixed_router import router as fixed_router')
        
        # If we found where routers are included, add ours
        if include_router_loc >= 0:
            lines.insert(include_router_loc + 1, 'app.include_router(fixed_router)')
        # Otherwise add it after app creation
        elif app_loc >= 0:
            lines.insert(app_loc + 1, 'app.include_router(fixed_router)')
        else:
            # Last resort - add at the end
            lines.append('# Adding fixed router')
            lines.append('try:')
            lines.append('    app.include_router(fixed_router)')
            lines.append('except Exception as e:')
            lines.append('    print(f"Error including fixed router: {e}")')
        
        # Write updated content
        with open(main_path, 'w') as f:
            f.write('\\n'.join(lines))
        
        print("Successfully updated main.py to include fixed router")
        return True
    else:
        print("Could not find appropriate place to insert import in main.py")
        return False

# Run the update
update_main()
"""

# Save these files
with open("fixed_router.py", "w") as f:
    f.write(router_code)

with open("update_main.py", "w") as f:
    f.write(main_updater)

# Copy the files to the container
print("Copying fixed router to API container...")
subprocess.run(["docker", "cp", "fixed_router.py", "api:/app/"], check=True)

print("Copying main updater to API container...")
subprocess.run(["docker", "cp", "update_main.py", "api:/app/"], check=True)

# Run the update script
print("Updating main.py to include our fixed router...")
result = subprocess.run(["docker", "exec", "api", "python", "/app/update_main.py"], 
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"Errors: {result.stderr}")

# Restart the API container
print("Restarting API container...")
subprocess.run(["docker", "restart", "api"], check=True)

# Wait for the API to restart
print("Waiting for API to restart...")
time.sleep(10)

print("Fix complete! The API should now work correctly.")