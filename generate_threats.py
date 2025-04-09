import subprocess
import webbrowser
import time
import os
import sys
import socket

def check_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_api():
    """Run the standalone API"""
    print("Starting the threat detection API...")
    
    # Check if port is already in use
    if check_port_in_use(8080):
        print("Port 8080 is already in use. API might already be running.")
        return True
    
    # Start the API process
    try:
        api_process = subprocess.Popen([sys.executable, 'standalone_api.py'], 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
        
        # Wait for API to start
        print("Waiting for API to start...")
        for i in range(10):  # Try for 5 seconds
            if check_port_in_use(8080):
                print("API is running!")
                return True
            time.sleep(0.5)
        
        # Check if process is still running
        if api_process.poll() is not None:
            print("API process exited with code:", api_process.returncode)
            print("STDOUT:", api_process.stdout.read())
            print("STDERR:", api_process.stderr.read())
            return False
            
        return True
    except Exception as e:
        print(f"Error starting API: {e}")
        return False

def open_dashboard():
    """Open the dashboard in a browser"""
    dashboard_path = os.path.abspath('threat_detection_dashboard.html')
    dashboard_url = f'file://{dashboard_path}'
    
    print(f"Opening dashboard at: {dashboard_url}")
    webbrowser.open(dashboard_url)

if __name__ == "__main__":
    # Run the API
    if run_api():
        # Open the dashboard
        open_dashboard()
        print("\nThreat Detection System is running!")
        print("Use Ctrl+C to exit")
        
        try:
            # Keep script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        print("Failed to start the Threat Detection System")