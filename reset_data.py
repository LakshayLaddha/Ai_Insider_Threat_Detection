#!/usr/bin/env python3
import sqlite3
import os
import sys

def reset_security_data():
    """Reset login activities, alerts and security-related data"""
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Resetting security monitoring data...")
        
        # Get table names from SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # Reset login activities if the table exists
        if 'login_activities' in table_names:
            cursor.execute("DELETE FROM login_activities")
            print(f"✓ Cleared login_activities table")
            
        # Reset alerts if the table exists
        if 'alerts' in table_names:
            cursor.execute("DELETE FROM alerts")
            print(f"✓ Cleared alerts table")
        
        # Reset file activities if the table exists
        if 'file_activities' in table_names:
            cursor.execute("DELETE FROM file_activities")
            print(f"✓ Cleared file_activities table")
        
        # Reset any other security-related tables
        for table in ['security_events', 'threat_logs', 'notifications']:
            if table in table_names:
                cursor.execute(f"DELETE FROM {table}")
                print(f"✓ Cleared {table} table")
        
        # Commit the changes
        conn.commit()
        print("\nAll security data has been reset. Dashboard should now show zero activities.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error resetting data: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_security_data()