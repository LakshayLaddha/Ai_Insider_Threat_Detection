#!/usr/bin/env python3
"""
Script to clear all activity data from the database.
Run this before starting fresh monitoring.
"""
import os
import sys
import sqlite3

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def clear_database():
    """Clear all activity data from the database"""
    try:
        # Connect to the database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel.db")
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️  Clearing database...")
        
        # Clear all activity tables
        tables_to_clear = [
            ("alerts", "security alerts"),
            ("file_activities", "file activities"),
            ("login_activities", "login activities")
        ]
        
        for table_name, description in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                count = cursor.rowcount
                print(f"   ✓ Cleared {count} {description}")
            except Exception as e:
                print(f"   ✗ Error clearing {table_name}: {str(e)}")
        
        # Commit the changes
        conn.commit()
        
        # Show current counts (should all be 0)
        print("\n📊 Current database status:")
        for table_name, description in tables_to_clear:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {description}: {count}")
        
        conn.close()
        
        print("\n✅ Database cleared successfully!")
        print("   You can now start fresh monitoring with threat_simulator.py")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("=== Sentinel Security Database Cleanup ===\n")
    
    # Confirm with user
    response = input("⚠️  This will delete ALL alerts and activity data. Continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Cancelled.")
        return
    
    clear_database()

if __name__ == "__main__":
    main()