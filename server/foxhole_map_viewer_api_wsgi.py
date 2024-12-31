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
try:
				print(f"[{datetime.now()}] Starting war reports updater")
				subprocess.Popen(['python3', script_path])
except Exception as e:
				print(f"Error starting updater: {str(e)}")

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