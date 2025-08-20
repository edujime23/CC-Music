import os
import json
from http.server import BaseHTTPRequestHandler

# Define the path to the music directory relative to this file's location
BASE_MUSIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'music'))

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        all_file_paths = []
        
        if not os.path.isdir(BASE_MUSIC_DIR):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = json.dumps({'error': 'Music directory not found on server.'})
            self.wfile.write(error_message.encode('utf-8'))
            return

        for root, dirs, files in os.walk(BASE_MUSIC_DIR):
            for filename in files:
                relative_path = os.path.relpath(os.path.join(root, filename), BASE_MUSIC_DIR)
                web_path = os.path.join('/music', relative_path).replace(os.sep, '/')
                all_file_paths.append(web_path)
        
        # --- Send the JSON response ---
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Convert the Python list to a JSON string and write it to the response
        json_response = json.dumps(all_file_paths)
        self.wfile.write(json_response.encode('utf-8'))
        return
