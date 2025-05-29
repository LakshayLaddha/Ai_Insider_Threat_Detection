#!/usr/bin/env python3
import requests
import random
import time
import sqlite3
import os
import json
import argparse
import sys
import threading
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@123"

# Login credentials for simulation
VALID_USERS = [
    {"email": "admin@example.com", "password": "Admin@123"},
    {"email": "user1@example.com", "password": "password123"},
    {"email": "user2@example.com", "password": "password123"}
]

# IP addresses for simulation
NORMAL_IPS = ["192.168.1.100", "127.0.0.1", "10.0.0.5", "172.16.0.10"]
SUSPICIOUS_IPS = ["203.0.113.5", "91.108.23.45", "185.176.43.101", "45.227.253.98"]

# User agents for simulation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G970U) AppleWebKit/537.36"
]

# File paths for simulation
NORMAL_FILES = [
    "/documents/report.pdf",
    "/images/presentation.pptx",
    "/projects/code.zip",
    "/shared/meeting_notes.docx"
]

SENSITIVE_FILES = [
    "/hr/employee_database.xlsx",
    "/finance/annual_report.pdf",
    "/security/access_logs.csv",
    "/confidential/patents.docx"
]

FILE_ACTIONS = ["VIEW", "DOWNLOAD", "UPLOAD", "DELETE", "MODIFY"]

# Location data for IP addresses
IP_LOCATIONS = {
    "192.168.1.100": {"city": "New York", "country": "United States", "latitude": 40.7128, "longitude": -74.0060},
    "127.0.0.1": {"city": "Localhost", "country": "Internal", "latitude": 0, "longitude": 0},
    "10.0.0.5": {"city": "San Francisco", "country": "United States", "latitude": 37.7749, "longitude": -122.4194},
    "172.16.0.10": {"city": "Chicago", "country": "United States", "latitude": 41.8781, "longitude": -87.6298},
    "203.0.113.5": {"city": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6173},
    "91.108.23.45": {"city": "Beijing", "country": "China", "latitude": 39.9042, "longitude": 116.4074},
    "185.176.43.101": {"city": "Tehran", "country": "Iran", "latitude": 35.6892, "longitude": 51.3890},
    "45.227.253.98": {"city": "Lagos", "country": "Nigeria", "latitude": 6.5244, "longitude": 3.3792}
}

# Global variables
admin_token = None
simulation_running = False
threat_percentage = 20  # Default threat percentage
total_events = 0
threat_events = 0

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def login_admin():
    """Login as admin to get token for API operations"""
    global admin_token
    try:
        form_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(
            f"{BASE_URL}/login",
            data=form_data
        )
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
            print("✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error logging in as admin: {str(e)}")
        return False

def get_user_id(email):
    """Get user ID from email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None

def create_user_if_not_exists(email):
    """Create user if doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return True
    
    # Create user
    try:
        from app.utils.security import get_password_hash
        hashed_password = get_password_hash("password123")
    except:
        # Simple fallback hash
        hashed_password = "$2b$12$dummy.hash.for.testing.only"
    
    username = email.split('@')[0]
    cursor.execute("""
        INSERT INTO users (email, username, hashed_password, full_name, is_active, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, username, hashed_password, username.title(), True, False, datetime.utcnow()))
    
    conn.commit()
    conn.close()
    return True

def log_activity_direct(user_email, ip_address, success, user_agent, is_anomalous=False):
    """Log login activity directly to database"""
    try:
        # Ensure user exists
        create_user_if_not_exists(user_email)
        user_id = get_user_id(user_email)
        if not user_id:
            return False
            
        # Get location info
        location = IP_LOCATIONS.get(ip_address, {"city": "Unknown", "country": "Unknown", "latitude": 0, "longitude": 0})
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Current time
        now = datetime.utcnow()
        
        # Insert login activity
        cursor.execute("""
            INSERT INTO login_activities (
                user_id, user_email, ip_address, user_agent,
                country, city, coordinates, timestamp, success, is_anomalous
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_email,
            ip_address,
            user_agent,
            location["country"],
            location["city"],
            f"{location['latitude']},{location['longitude']}",
            now,
            success,
            is_anomalous
        ))
        
        # If this is a suspicious login, also create an alert
        if is_anomalous or ip_address in SUSPICIOUS_IPS:
            severity = "high" if is_anomalous else "medium"
            message = f"Suspicious login attempt from {location['city']}, {location['country']}"
            
            cursor.execute("""
                INSERT INTO alerts (
                    user_id, alert_type, severity, message,
                    source_ip, location, timestamp, resolved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                "login",
                severity,
                message,
                ip_address,
                location['country'],
                now,
                False
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error logging activity to database: {str(e)}")
        return False

def log_file_activity_direct(user_email, file_path, action, ip_address, is_anomalous=False):
    """Log file activity directly to database"""
    try:
        # Ensure user exists
        create_user_if_not_exists(user_email)
        user_id = get_user_id(user_email)
        if not user_id:
            return False
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Current time
        now = datetime.utcnow()
        
        # Insert file activity
        cursor.execute("""
            INSERT INTO file_activities (
                user_id, user_email, file_path, action,
                timestamp, ip_address, is_anomalous, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_email,
            file_path,
            action,
            now,
            ip_address,
            is_anomalous,
            f"File {action.lower()} by {user_email}"
        ))
        
        # If this is suspicious activity, create an alert
        if is_anomalous or file_path in SENSITIVE_FILES:
            severity = "critical" if action == "DELETE" and file_path in SENSITIVE_FILES else "high"
            message = f"Suspicious file activity: {action} on {file_path}"
            
            cursor.execute("""
                INSERT INTO alerts (
                    user_id, alert_type, severity, message,
                    source_ip, location, timestamp, resolved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                "file",
                severity,
                message,
                ip_address,
                "Unknown",
                now,
                False
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error logging file activity to database: {str(e)}")
        return False

def simulate_normal_login():
    """Simulate a normal, legitimate login"""
    global total_events
    user = random.choice(VALID_USERS)
    user_agent = random.choice(USER_AGENTS)
    ip = random.choice(NORMAL_IPS)
    
    # Log to database
    log_result = log_activity_direct(user["email"], ip, True, user_agent, False)
    
    total_events += 1
    print(f"✅ Normal login from {ip} as {user['email']}")
    return True

def simulate_suspicious_login():
    """Simulate a suspicious login attempt"""
    global total_events, threat_events
    
    user = random.choice(VALID_USERS)
    user_agent = random.choice(USER_AGENTS)
    ip = random.choice(SUSPICIOUS_IPS)
    success = random.choice([True, False])
    
    # Log to database
    log_result = log_activity_direct(user["email"], ip, success, user_agent, True)
    
    total_events += 1
    threat_events += 1
    result = "⚠️ SUSPICIOUS" if success else "🚫 BLOCKED"
    print(f"{result} Suspicious login from {ip} as {user['email']}")
    return True

def simulate_failed_login():
    """Simulate a failed login attempt"""
    global total_events
    user = random.choice(VALID_USERS)
    user_agent = random.choice(USER_AGENTS)
    ip = random.choice(NORMAL_IPS)
    
    # Log to database
    log_result = log_activity_direct(user["email"], ip, False, user_agent, False)
    
    total_events += 1
    print(f"❌ Failed login attempt from {ip} as {user['email']}")
    return True

def simulate_normal_file_activity():
    """Simulate normal file activity"""
    global total_events
    user = random.choice(VALID_USERS)
    file_path = random.choice(NORMAL_FILES)
    action = random.choice(["VIEW", "DOWNLOAD", "UPLOAD"])
    ip = random.choice(NORMAL_IPS)
    
    # Log to database
    log_result = log_file_activity_direct(user["email"], file_path, action, ip, False)
    
    total_events += 1
    print(f"📄 Normal file activity: {user['email']} {action} {file_path}")
    return True

def simulate_suspicious_file_activity():
    """Simulate suspicious file activity"""
    global total_events, threat_events
    user = random.choice(VALID_USERS)
    file_path = random.choice(SENSITIVE_FILES)
    action = random.choice(FILE_ACTIONS)
    ip = random.choice(SUSPICIOUS_IPS + NORMAL_IPS)
    
    # Log to database
    log_result = log_file_activity_direct(user["email"], file_path, action, ip, True)
    
    total_events += 1
    threat_events += 1
    print(f"⚠️ Suspicious file activity: {user['email']} {action} {file_path}")
    return True

def update_stats():
    """Update and display current statistics"""
    global total_events, threat_events
    if total_events == 0:
        current_percentage = 0
    else:
        current_percentage = (threat_events / total_events) * 100
    
    print("\n--- CURRENT SIMULATION STATISTICS ---")
    print(f"Total events: {total_events}")
    print(f"Threat events: {threat_events}")
    print(f"Current threat percentage: {current_percentage:.1f}%")
    print(f"Target threat percentage: {threat_percentage}%")
    print("------------------------------------\n")

def simulation_thread():
    """Thread function to run the simulation"""
    global simulation_running, total_events, threat_events, threat_percentage
    
    print("🚀 Starting security event simulation...")
    
    while simulation_running:
        # Determine if this iteration should generate a threat or normal event
        if total_events > 0:
            current_percentage = (threat_events / total_events) * 100
        else:
            current_percentage = 0
            
        # Mix of different event types
        event_type = random.choices(
            ['normal_login', 'failed_login', 'suspicious_login', 'normal_file', 'suspicious_file'],
            weights=[40, 15, 10, 25, 10] if current_percentage >= threat_percentage else [30, 10, 15, 20, 25],
            k=1
        )[0]
        
        if event_type == 'normal_login':
            simulate_normal_login()
        elif event_type == 'failed_login':
            simulate_failed_login()
        elif event_type == 'suspicious_login':
            simulate_suspicious_login()
        elif event_type == 'normal_file':
            simulate_normal_file_activity()
        else:
            simulate_suspicious_file_activity()
        
        # Sleep for a random interval
        time.sleep(random.uniform(0.5, 2))
        
        # Periodically update stats
        if total_events % 10 == 0:
            update_stats()

def start_simulation():
    """Start the simulation in a separate thread"""
    global simulation_running
    
    if not login_admin():
        print("Cannot start simulation without admin access")
        return
    
    if simulation_running:
        print("Simulation is already running")
        return
    
    simulation_running = True
    thread = threading.Thread(target=simulation_thread)
    thread.daemon = True
    thread.start()
    print("Simulation started in background. Use 'set' to change the threat percentage.")

def stop_simulation():
    """Stop the running simulation"""
    global simulation_running
    
    if not simulation_running:
        print("No simulation is running")
        return
    
    simulation_running = False
    print("Stopping simulation...")
    time.sleep(1)  # Give time for thread to finish
    update_stats()
    print("Simulation stopped")

def reset_stats():
    """Reset the simulation statistics"""
    global total_events, threat_events
    total_events = 0
    threat_events = 0
    print("Statistics reset")
    update_stats()

def set_threat_percentage(percentage):
    """Set the target threat percentage"""
    global threat_percentage
    
    try:
        percentage = float(percentage)
        if percentage < 0 or percentage > 100:
            print("Percentage must be between 0 and 100")
            return
        
        threat_percentage = percentage
        print(f"Threat percentage set to {threat_percentage}%")
    except ValueError:
        print("Invalid percentage value")

def clear_database():
    """Clear all activity data from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear tables
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM file_activities")
        cursor.execute("DELETE FROM login_activities")
        
        conn.commit()
        conn.close()
        
        print("✅ Database cleared successfully")
        reset_stats()
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")

def show_help():
    """Display available commands"""
    print("\nAvailable commands:")
    print("  start       - Start the simulation")
    print("  stop        - Stop the simulation")
    print("  stats       - Show current statistics")
    print("  reset       - Reset the statistics counters")
    print("  clear       - Clear all data from database")
    print("  set [n]     - Set the target threat percentage to [n]")
    print("  help        - Show this help message")
    print("  exit        - Exit the simulator\n")

def main():
    """Main function to run the interactive simulator"""
    global simulation_running
    
    print("\n==== Sentinel Security Threat Simulator ====")
    print("Type 'help' for a list of commands")
    
    # Ask if user wants to clear data
    response = input("\nDo you want to clear existing data before starting? (y/n): ").strip().lower()
    if response == 'y':
        clear_database()
    
    while True:
        try:
            cmd = input("\nsimulator> ").strip().lower().split()
            
            if not cmd:
                continue
                
            if cmd[0] == "start":
                start_simulation()
            
            elif cmd[0] == "stop":
                stop_simulation()
            
            elif cmd[0] == "stats":
                update_stats()
            
            elif cmd[0] == "reset":
                reset_stats()
            
            elif cmd[0] == "clear":
                if simulation_running:
                    print("Please stop the simulation before clearing the database")
                else:
                    clear_database()
            
            elif cmd[0] == "set" and len(cmd) > 1:
                set_threat_percentage(cmd[1])
            
            elif cmd[0] == "help":
                show_help()
            
            elif cmd[0] in ["exit", "quit"]:
                if simulation_running:
                    stop_simulation()
                print("Exiting simulator...")
                break
                
            else:
                print("Unknown command. Type 'help' for assistance.")
                
        except KeyboardInterrupt:
            print("\nInterrupted. Use 'exit' to quit properly.")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("Simulator closed")

if __name__ == "__main__":
    main()