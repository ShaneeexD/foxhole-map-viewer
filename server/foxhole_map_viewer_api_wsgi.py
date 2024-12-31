import sys
import os
import subprocess
from datetime import datetime

# Add the project directory to the Python path
project_dir = '/home/ShaneeexD/FoxholeMapViewerAPI'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set up environment variables if needed
os.environ['PYTHONPATH'] = project_dir

# Start the background updater as a separate process
script_path = '/home/ShaneeexD/FoxholeMapViewerAPI/update_war_reports.py'
updater_process = None

def start_updater():
				global updater_process
				try:
								# Check if updater is already running
								if updater_process and updater_process.poll() is None:
												print(f"[{datetime.now()}] Updater already running (PID: {updater_process.pid})")
												return
								
								print(f"[{datetime.now()}] Starting war reports updater")
								updater_process = subprocess.Popen(
												['python3', script_path],
												stdout=subprocess.PIPE,
												stderr=subprocess.PIPE
								)
								print(f"[{datetime.now()}] Updater started (PID: {updater_process.pid})")
				except Exception as e:
								print(f"[{datetime.now()}] Error starting updater: {str(e)}")

# Start the updater when WSGI loads
start_updater()

# Add periodic check to ensure updater is running
import time
import threading

def monitor_updater():
				while True:
								if updater_process is None or updater_process.poll() is not None:
												print(f"[{datetime.now()}] Updater not running, restarting...")
												start_updater()
								time.sleep(60)  # Check every minute

# Start monitor thread
monitor_thread = threading.Thread(target=monitor_updater, daemon=True)
monitor_thread.start()

# WSGI application object
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    try:
        file_path = '/home/ShaneeexD/FoxholeMapViewerAPI/war_reports.json'
        with open(file_path, 'r') as f:
            json_data = f.read()
            # Add last modified timestamp to response
            last_modified = os.path.getmtime(file_path)
            headers.append(('Last-Modified', datetime.fromtimestamp(last_modified).strftime('%a, %d %b %Y %H:%M:%S GMT')))
            start_response(status, headers)
            return [json_data.encode('utf-8')]
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f"Error reading war reports: {str(e)}".encode('utf-8')]