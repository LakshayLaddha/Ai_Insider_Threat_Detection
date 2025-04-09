
import pandas as pd
from datetime import datetime

def extract_features(log_entry):
    # Initialize features dictionary
    features = {}
    
    # Make sure date field exists
    if 'date' not in log_entry and 'timestamp' in log_entry:
        try:
            timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
            log_entry['date'] = timestamp.strftime('%Y-%m-%d')
        except Exception:
            log_entry['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Time features
    try:
        if 'timestamp' in log_entry:
            timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
            features['hour'] = timestamp.hour
            features['day_of_week'] = timestamp.weekday()
        else:
            features['hour'] = log_entry.get('hour', datetime.now().hour)
            features['day_of_week'] = log_entry.get('day_of_week', datetime.now().weekday())
    except Exception:
        features['hour'] = log_entry.get('hour', datetime.now().hour)
        features['day_of_week'] = log_entry.get('day_of_week', datetime.now().weekday())
    
    # User features
    user_id = log_entry.get('user_id', '').lower()
    features['user_id_admin'] = 1 if 'admin' in user_id else log_entry.get('user_id_admin', 0)
    features['user_id_system'] = 1 if 'system' in user_id else log_entry.get('user_id_system', 0)
    features['user_id_lakshay'] = 1 if 'lakshay' in user_id else log_entry.get('user_id_lakshay', 0)
    features['user_id_other'] = 1 if not any(x in user_id for x in ['admin', 'system', 'lakshay']) else log_entry.get('user_id_other', 0)
    
    # Action features
    action = log_entry.get('action', '').upper()
    features['action_read'] = 1 if action == 'READ' else log_entry.get('action_read', 0)
    features['action_write'] = 1 if action == 'WRITE' else log_entry.get('action_write', 0)
    features['action_login'] = 1 if action == 'LOGIN' else log_entry.get('action_login', 0)
    features['action_download'] = 1 if action == 'DOWNLOAD' else log_entry.get('action_download', 0)
    features['action_delete'] = 1 if action == 'DELETE' else log_entry.get('action_delete', 0)
    features['action_modify'] = 1 if action == 'MODIFY' else log_entry.get('action_modify', 0)
    features['action_execute'] = 1 if action == 'EXECUTE' else log_entry.get('action_execute', 0)
    
    # Resource features
    resource = log_entry.get('resource', '').upper()
    features['resource_financial'] = 1 if 'FINANCIAL' in resource else log_entry.get('resource_financial', 0)
    features['resource_customer'] = 1 if 'CUSTOMER' in resource else log_entry.get('resource_customer', 0)
    features['resource_employee'] = 1 if 'EMPLOYEE' in resource else log_entry.get('resource_employee', 0)
    features['resource_source'] = 1 if 'SOURCE' in resource else log_entry.get('resource_source', 0)
    features['resource_infrastructure'] = 1 if 'INFRASTRUCTURE' in resource else log_entry.get('resource_infrastructure', 0)
    features['resource_security'] = 1 if 'SECURITY' in resource else log_entry.get('resource_security', 0)
    
    # Other features
    features['data_size'] = log_entry.get('data_size', 0)
    
    # Suspicious IP detection
    ip_address = log_entry.get('ip_address', '')
    suspicious_ips = ['45.227.253.77', '103.152.36.49', '185.176.27.132']
    features['is_suspicious_ip'] = 1 if ip_address in suspicious_ips else log_entry.get('is_suspicious_ip', 0)
    
    return features
