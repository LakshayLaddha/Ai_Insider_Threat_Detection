#!/usr/bin/env python3
import sqlite3
import os
import sys
import requests
import time

def reset_database_completely():
    """Reset ALL relevant database tables and force refresh"""
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Performing complete system reset...")
        
        # 1. Get all tables from SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # 2. Reset all monitoring-related tables
        monitoring_tables = [
            'login_activities', 'alerts', 'file_activities', 
            'security_events', 'threat_logs', 'notifications',
            'system_metrics', 'audit_logs', 'access_logs',
            'events', 'user_activities'
        ]
        
        for table in monitoring_tables:
            if table in table_names:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"✓ Cleared {table} table")
                except Exception as e:
                    print(f"Error clearing {table}: {str(e)}")
        
        # 3. Reset user last_login timestamps
        if 'users' in table_names:
            try:
                cursor.execute("UPDATE users SET last_login_at = NULL")
                print("✓ Reset user last_login timestamps")
            except Exception as e:
                print(f"Error resetting user timestamps: {str(e)}")
        
        # 4. Add dummy "system reset" record for logging
        if 'system_logs' in table_names:
            try:
                now = time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO system_logs (log_type, message, created_at) VALUES (?, ?, ?)",
                    ("SYSTEM", "Dashboard data reset performed", now)
                )
                print("✓ Added system reset log entry")
            except Exception as e:
                print(f"Could not add system log: {str(e)}")
        
        # 5. Commit all changes
        conn.commit()
        print("\n✅ Database reset complete!\n")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during reset: {str(e)}")
    finally:
        conn.close()

def restart_application():
    """Try to trigger application restart if supported"""
    print("Attempting to refresh application state...")
    
    try:
        # Try hitting a refresh endpoint if your app has one
        response = requests.post("http://localhost:8000/api/v1/system/refresh-cache", 
                                 timeout=2)
        if response.status_code == 200:
            print("✓ Application cache refresh triggered")
        else:
            print("Could not trigger application refresh automatically")
    except:
        print("No automatic refresh endpoint available")
    
    print("\n⚠️ IMPORTANT NEXT STEPS:")
    print("1. Restart the application server:")
    print("   CTRL+C to stop the current server")
    print("   Then run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Refresh your browser window completely (CTRL+F5)")
    print("3. Log out and log back in to reset session data\n")

if __name__ == "__main__":
    reset_database_completely()
    restart_application()
    
    print("Ready to run the simulator! Once you've restarted the server and refreshed your browser,")
    print("use: python improved_simulator.py")