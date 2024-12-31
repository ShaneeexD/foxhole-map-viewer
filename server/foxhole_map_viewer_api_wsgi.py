import sys
import os
from datetime import datetime

# Add the path to your project directory
sys.path.insert(0, '/home/ShaneeexD/FoxholeMapViewerAPI')

def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]

    try:
        # Serve the JSON file
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
