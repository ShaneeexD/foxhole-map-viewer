import sys
import os
import threading
from datetime import datetime

# Add the project directory to the Python path
project_dir = '/home/ShaneeexD/FoxholeMapViewerAPI'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set up environment variables if needed
os.environ['PYTHONPATH'] = project_dir

# Import the update function
from update_war_reports import update_war_reports, schedule_update

# Start the background updater
print(f"[{datetime.now()}] Starting war reports updater")
schedule_update()

# WSGI application object
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b"Foxhole Map Viewer API is running. War reports are being updated every 10 minutes."]