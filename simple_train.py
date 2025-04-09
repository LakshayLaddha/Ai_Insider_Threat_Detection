import pandas as pd
import numpy as np
import os
import json
import joblib
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Create output directory
MODEL_DIR = "ml_model/trained_models"
os.makedirs(MODEL_DIR, exist_ok=True)

print("Generating synthetic training data...")

# Generate synthetic training data
users = ['user_1', 'user_2', 'user_3', 'admin', 'system', 'lakshay.laddha']
actions = ['READ', 'WRITE', 'LOGIN', 'DOWNLOAD', 'DELETE', 'MODIFY', 'EXECUTE']
resources = ['FINANCIAL_DATA', 'CUSTOMER_DATABASE', 'EMPLOYEE_RECORDS', 
            'SOURCE_CODE', 'INFRASTRUCTURE_CONFIG', 'SECURITY_KEYS']
normal_ips = ['192.168.1.105', '10.0.0.123', '172.16.0.5', '192.168.0.15']
suspicious_ips = ['45.227.253.77', '103.152.36.49', '185.176.27.132']

# Generate synthetic data
n_samples = 1000
data = []

# Normal behavior (80%)
for i in range(int(n_samples * 0.8)):
    hour = np.random.choice(range(8, 18))  # Business hours
    data_size = np.random.randint(1000, 100000)
    # Business hours, normal IPs, smaller data sizes
    data.append({
        'hour': hour,
        'day_of_week': np.random.randint(0, 5),  # Weekday
        'user_id_admin': 1 if np.random.choice(users) == 'admin' else 0,
        'user_id_system': 1 if np.random.choice(users) == 'system' else 0,
        'user_id_lakshay': 1 if np.random.choice(users) == 'lakshay.laddha' else 0,
        'user_id_other': 1 if np.random.choice(users) not in ['admin', 'system', 'lakshay.laddha'] else 0,
        'action_read': 1 if np.random.choice(actions[:3]) == 'READ' else 0,
        'action_write': 1 if np.random.choice(actions[:3]) == 'WRITE' else 0,
        'action_login': 1 if np.random.choice(actions[:3]) == 'LOGIN' else 0,
        'action_download': 0,
        'action_delete': 0,
        'action_modify': 0,
        'action_execute': 0,
        'resource_financial': 1 if np.random.choice(resources[:3]) == 'FINANCIAL_DATA' else 0,
        'resource_customer': 1 if np.random.choice(resources[:3]) == 'CUSTOMER_DATABASE' else 0,
        'resource_employee': 1 if np.random.choice(resources[:3]) == 'EMPLOYEE_RECORDS' else 0,
        'resource_source': 0,
        'resource_infrastructure': 0,
        'resource_security': 0,
        'data_size': data_size,
        'is_suspicious_ip': 0
    })

# Anomalous behavior (20%)
for i in range(int(n_samples * 0.2)):
    hour = np.random.choice([0, 1, 2, 3, 4, 5, 22, 23])  # Off-hours
    data_size = np.random.randint(500000, 10000000)  # Large data transfers
    # Off-hours, suspicious IPs, sensitive resources, suspicious actions
    data.append({
        'hour': hour,
        'day_of_week': np.random.choice([5, 6]),  # Weekend
        'user_id_admin': 1 if np.random.choice(users) == 'admin' else 0,
        'user_id_system': 1 if np.random.choice(users) == 'system' else 0,
        'user_id_lakshay': 1 if np.random.choice(users) == 'lakshay.laddha' else 0,
        'user_id_other': 1 if np.random.choice(users) not in ['admin', 'system', 'lakshay.laddha'] else 0,
        'action_read': 0,
        'action_write': 0,
        'action_login': 0,
        'action_download': 1 if np.random.choice(actions[3:]) == 'DOWNLOAD' else 0,
        'action_delete': 1 if np.random.choice(actions[3:]) == 'DELETE' else 0,
        'action_modify': 1 if np.random.choice(actions[3:]) == 'MODIFY' else 0,
        'action_execute': 1 if np.random.choice(actions[3:]) == 'EXECUTE' else 0,
        'resource_financial': 0,
        'resource_customer': 0,
        'resource_employee': 0,
        'resource_source': 1 if np.random.choice(resources[3:]) == 'SOURCE_CODE' else 0,
        'resource_infrastructure': 1 if np.random.choice(resources[3:]) == 'INFRASTRUCTURE_CONFIG' else 0,
        'resource_security': 1 if np.random.choice(resources[3:]) == 'SECURITY_KEYS' else 0,
        'data_size': data_size,
        'is_suspicious_ip': 1
    })

# Convert to DataFrame
df = pd.DataFrame(data)
print(f"Generated {len(df)} training records")

# Feature scaling
print("Training model...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Train Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.2,  # Expected proportion of anomalies
    random_state=42
)
model.fit(X_scaled)

# Save model files
print("Saving model files...")

# Save the model
joblib.dump(model, f"{MODEL_DIR}/isolation_forest.pkl")

# Save the scaler
joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

# Create and save metadata
feature_names = df.columns.tolist()
metadata = {
    "model_type": "IsolationForest",
    "training_date": datetime.now().isoformat(),
    "num_features": len(feature_names),
    "feature_names": feature_names,
    "n_estimators": 100,
    "contamination": 0.2,
    "threshold": -0.2  # Default threshold for detecting anomalies
}

with open(f"{MODEL_DIR}/model_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print("Model training completed!")
print(f"Files saved to {MODEL_DIR}:")
print(f"  - isolation_forest.pkl")
print(f"  - scaler.pkl")
print(f"  - model_metadata.json")