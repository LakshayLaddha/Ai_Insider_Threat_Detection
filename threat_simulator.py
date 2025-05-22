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
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@123"

# Login credentials for simulation
VALID_USERS = [
    {"email": "admin@example.com", "password": "admin123"},
    {"email": "user1@example.com", "password": "password123"},
    {"email": "user2@example.com", "password": "password123"}
]

# IP addresses for simulation
NORMAL_IPS = ["192.168.1.100", "127.0.0.1", "10.0.0.5"]
SUSPICIOUS_IPS = ["203.0.113.5", "91.108.23.45", "185.176.43.101", "45.227.253.98"]

# User agents for simulation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G970U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36"
]

# Location data for IP addresses
IP_LOCATIONS = {
    "192.168.1.100": {"city": "Local Network", "country": "Internal", "latitude": 0, "longitude": 0},
    "127.0.0.1": {"city": "Localhost", "country": "Internal", "latitude": 0, "longitude": 0},
    "10.0.0.5": {"city": "Office Network", "country": "Internal", "latitude": 0, "longitude": 0},
    "203.0.113.5": {"city": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6173},
    "91.108.23.45": {"city": "Beijing", "country": "China", "latitude": 39.9042, "longitude": 116.4074},
    "185.176.43.101": {"city": "Pyongyang", "country": "North Korea", "latitude": 39.0392, "longitude": 125.7625},
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
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
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

def log_activity_direct(user_email, ip_address, status, user_agent):
    """Log activity directly to database to ensure dashboard sees it"""
    try:
        # Get user ID from email
        user_id = get_user_id(user_email)
        if not user_id:
            print(f"User with email {user_email} not found in database")
            return False
            
        # Get location info
        location = IP_LOCATIONS.get(ip_address, {"city": "Unknown", "country": "Unknown", "latitude": 0, "longitude": 0})
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Current time
        now = datetime.utcnow().isoformat()
        
        # Insert login activity
        cursor.execute("""
            INSERT INTO login_activities (
                user_id, login_time, ip_address, user_agent,
                location_city, location_country, 
                latitude, longitude, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            now,
            ip_address,
            user_agent,
            location["city"],
            location["country"],
            location["latitude"],
            location["longitude"],
            status
        ))
        
        # If this is a suspicious login, also create an alert
        if ip_address in SUSPICIOUS_IPS:
            alert_level = "medium" if status == "success" else "high"
            alert_message = f"Suspicious login from {location['city']}, {location['country']}" if status == "success" else f"Failed login attempt from {location['city']}, {location['country']}"
            
            cursor.execute("""
                INSERT INTO alerts (
                    user_id, alert_type, alert_level, message,
                    created_at, updated_at, is_resolved
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                "suspicious_login",
                alert_level,
                alert_message,
                now,
                now,
                0  # Not resolved
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error logging activity to database: {str(e)}")
        return False

def simulate_normal_login():
    """Simulate a normal, legitimate login"""
    global total_events
    user = random.choice(VALID_USERS)
    user_agent = random.choice(USER_AGENTS)
    
    # Choose a normal IP
    ip = random.choice(NORMAL_IPS)
    
    try:
        # Try API login first
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": user["email"], "password": user["password"]},
            headers={"User-Agent": user_agent, "X-Forwarded-For": ip}
        )
        
        success = response.status_code == 200
        status = "success" if success else "failure"
        
        # Log to database directly to ensure dashboard sees it
        log_result = log_activity_direct(user["email"], ip, status, user_agent)
        
        total_events += 1
        result = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{result} Normal login from {ip} as {user['email']}")
        return success
    except Exception as e:
        print(f"❌ Error simulating normal login: {str(e)}")
        return False

def simulate_suspicious_login():
    """Simulate a suspicious login attempt"""
    global total_events, threat_events
    
    # Choose whether to use valid credentials
    use_valid = random.choice([True, False])
    
    if use_valid:
        user = random.choice(VALID_USERS)
        password = user["password"]
    else:
        user = random.choice(VALID_USERS)
        password = "wrong" + str(random.randint(100, 999))
    
    user_agent = random.choice(USER_AGENTS)
    ip = random.choice(SUSPICIOUS_IPS)
    
    try:
        # Try API login
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": user["email"], "password": password},
            headers={"User-Agent": user_agent, "X-Forwarded-For": ip}
        )
        
        success = response.status_code == 200
        status = "success" if success else "failure"
        
        # Log to database directly
        log_result = log_activity_direct(user["email"], ip, status, user_agent)
        
        total_events += 1
        threat_events += 1
        result = "⚠️ SUSPICIOUS" if success else "🚫 BLOCKED"
        print(f"{result} Suspicious login from {ip} as {user['email']}")
        return True
    except Exception as e:
        print(f"❌ Error simulating suspicious login: {str(e)}")
        return False

def simulate_failed_login():
    """Simulate a failed login attempt with invalid credentials"""
    global total_events
    user = random.choice(VALID_USERS)
    user_agent = random.choice(USER_AGENTS)
    ip = random.choice(NORMAL_IPS)
    
    try:
        # Try API login with wrong password
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": user["email"], "password": "wrongpassword" + str(random.randint(100, 999))},
            headers={"User-Agent": user_agent, "X-Forwarded-For": ip}
        )
        
        success = response.status_code == 200  # Should be false
        status = "success" if success else "failure"
        
        # Log to database directly
        log_result = log_activity_direct(user["email"], ip, status, user_agent)
        
        total_events += 1
        result = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{result} Failed login attempt from {ip} as {user['email']}")
        return True
    except Exception as e:
        print(f"❌ Error simulating failed login: {str(e)}")
        return False

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
            
        if current_percentage < threat_percentage:
            # Need more threats to reach target percentage
            simulate_suspicious_login()
        else:
            # Random selection with higher chance of normal events
            event_type = random.choices(
                ['normal', 'failed', 'suspicious'],
                weights=[70, 20, 10],
                k=1
            )[0]
            
            if event_type == 'normal':
                simulate_normal_login()
            elif event_type == 'failed':
                simulate_failed_login()
            else:
                simulate_suspicious_login()
        
        # Sleep for a random interval
        time.sleep(random.uniform(1.5, 3))
        
        # Periodically update stats
        if total_events % 5 == 0:
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

def show_help():
    """Display available commands"""
    print("\nAvailable commands:")
    print("  start       - Start the simulation")
    print("  stop        - Stop the simulation")
    print("  stats       - Show current statistics")
    print("  reset       - Reset the statistics counters")
    print("  set [n]     - Set the target threat percentage to [n]")
    print("  help        - Show this help message")
    print("  exit        - Exit the simulator\n")

def main():
    """Main function to run the interactive simulator"""
    global simulation_running
    
    print("\n==== Sentinel Security Threat Simulator ====")
    print("Type 'help' for a list of commands")
    
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