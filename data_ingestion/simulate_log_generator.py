import pandas as pd
import numpy as np
import datetime
import random
import json
import os
import uuid
from typing import List, Dict, Any

class CloudLogSimulator:
    """Generates simulated AWS CloudTrail-like logs with user activities."""
    
    def __init__(self, 
                 num_users: int = 20, 
                 days_of_data: int = 30,
                 anomaly_ratio: float = 0.05):
        """
        Initialize the simulator with configuration parameters.
        
        Args:
            num_users: Number of unique users to simulate
            days_of_data: Number of days of log data to generate
            anomaly_ratio: Percentage of logs that should be anomalous
        """
        self.num_users = num_users
        self.days_of_data = days_of_data
        self.anomaly_ratio = anomaly_ratio
        
        # Define possible values for categorical fields
        self.users = [f"user_{i}" for i in range(1, num_users + 1)]
        self.actions = ["LOGIN", "READ", "WRITE", "DELETE", "UPDATE", "DOWNLOAD", "UPLOAD"]
        self.resources = ["S3_BUCKET", "EC2_INSTANCE", "RDS_DATABASE", "LAMBDA_FUNCTION", 
                         "DYNAMODB_TABLE", "IAM_ROLE", "CLOUDWATCH_LOG"]
        
        # Generate a map of user -> usual IPs (each user typically uses 1-3 IPs)
        self.user_ips = {}
        for user in self.users:
            num_ips = random.randint(1, 3)
            self.user_ips[user] = [
                f"{random.randint(1, 255)}.{random.randint(1, 255)}."
                f"{random.randint(1, 255)}.{random.randint(1, 255)}"
                for _ in range(num_ips)
            ]
    
    def _generate_timestamps(self, num_logs: int) -> List[datetime.datetime]:
        """Generate realistic timestamps over the specified period."""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=self.days_of_data)
        
        # Random timestamps between start_date and end_date
        timestamps = [start_date + (end_date - start_date) * random.random() 
                     for _ in range(num_logs)]
        timestamps.sort()  # Sort chronologically
        return timestamps
    
    def _generate_normal_logs(self, num_logs: int) -> List[Dict[str, Any]]:
        """Generate normal (non-anomalous) log entries."""
        logs = []
        timestamps = self._generate_timestamps(num_logs)
        
        for timestamp in timestamps:
            # For normal logs, users access at reasonable hours with their usual IPs
            user = random.choice(self.users)
            hour = timestamp.hour
            
            # Normal users typically access during business hours (higher probability)
            if random.random() < 0.8:  # 80% of normal logs during business hours
                # Adjust timestamp to be during business hours (8am-6pm)
                business_hour = random.randint(8, 18)
                timestamp = timestamp.replace(hour=business_hour)
            
            log = {
                "id": str(uuid.uuid4()),
                "user_id": user,
                "action": random.choice(self.actions),
                "timestamp": timestamp.isoformat(),
                "resource": random.choice(self.resources),
                "ip_address": random.choice(self.user_ips[user]),  # Use one of user's usual IPs
                "data_size": random.randint(1, 100) * 1024,  # in KB
                "is_anomaly": False  # Label for training later
            }
            logs.append(log)
        
        return logs
    
    def _generate_anomalous_logs(self, num_logs: int) -> List[Dict[str, Any]]:
        """Generate anomalous log entries."""
        logs = []
        timestamps = self._generate_timestamps(num_logs)
        
        for timestamp in timestamps:
            user = random.choice(self.users)
            
            # Choose an anomaly type
            anomaly_type = random.choice([
                "odd_hour", "unusual_ip", "large_data", "unusual_action_pattern"
            ])
            
            if anomaly_type == "odd_hour":
                # Set timestamp to odd hours (midnight to 5am)
                timestamp = timestamp.replace(hour=random.randint(0, 5))
                ip_address = random.choice(self.user_ips[user])
                data_size = random.randint(1, 100) * 1024
                
            elif anomaly_type == "unusual_ip":
                # Use an IP not associated with this user
                other_users = [u for u in self.users if u != user]
                other_user = random.choice(other_users)
                ip_address = random.choice(self.user_ips[other_user])
                data_size = random.randint(1, 100) * 1024
                
            elif anomaly_type == "large_data":
                # Unusually large data transfer
                ip_address = random.choice(self.user_ips[user])
                data_size = random.randint(500, 2000) * 1024  # 500MB to 2GB
                
            else:  # unusual_action_pattern
                # Use a sensitive action like DELETE at an unusual frequency
                ip_address = random.choice(self.user_ips[user])
                data_size = random.randint(1, 100) * 1024
            
            log = {
                "id": str(uuid.uuid4()),
                "user_id": user,
                "action": "DELETE" if anomaly_type == "unusual_action_pattern" else random.choice(self.actions),
                "timestamp": timestamp.isoformat(),
                "resource": random.choice(self.resources),
                "ip_address": ip_address,
                "data_size": data_size,
                "is_anomaly": True,  # Label for training later
                "anomaly_type": anomaly_type  # For reference
            }
            logs.append(log)
        
        return logs
    
    def generate_logs(self, total_logs: int = 10000) -> pd.DataFrame:
        """Generate a mix of normal and anomalous logs."""
        # Calculate number of anomalous logs
        num_anomalous = int(total_logs * self.anomaly_ratio)
        num_normal = total_logs - num_anomalous
        
        # Generate logs
        normal_logs = self._generate_normal_logs(num_normal)
        anomalous_logs = self._generate_anomalous_logs(num_anomalous)
        
        # Combine and shuffle logs
        all_logs = normal_logs + anomalous_logs
        random.shuffle(all_logs)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_logs)
        
        # Sort by timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def save_logs(self, df: pd.DataFrame, output_dir: str = '../logs/', 
                  csv_filename: str = 'sample_logs.csv',
                  json_filename: str = 'sample_logs.json'):
        """Save generated logs to CSV and JSON."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as CSV
        csv_path = os.path.join(output_dir, csv_filename)
        df.to_csv(csv_path, index=False)
        
        # Save as JSON
        json_path = os.path.join(output_dir, json_filename)
        df.to_json(json_path, orient='records', lines=True)
        
        return csv_path, json_path

if __name__ == "__main__":
    # Example usage
    simulator = CloudLogSimulator(num_users=20, days_of_data=30, anomaly_ratio=0.05)
    logs_df = simulator.generate_logs(total_logs=10000)
    csv_path, json_path = simulator.save_logs(logs_df)
    
    print(f"Generated {len(logs_df)} log entries")
    print(f"Normal logs: {len(logs_df[~logs_df['is_anomaly']])}")
    print(f"Anomalous logs: {len(logs_df[logs_df['is_anomaly']])}")
    print(f"Logs saved to CSV: {csv_path}")
    print(f"Logs saved to JSON: {json_path}")
    
    # Display sample of the data
    print("\nSample log entries:")
    print(logs_df.head())