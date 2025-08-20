import os
import json
from http.server import BaseHTTPRequestHandler

# This path logic is correct because in the deployment, 'music' will be
# at the root, and this script will be in 'api/'.
BASE_MUSIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'music'))

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if not os.path.isdir(BASE_MUSIC_DIR):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = json.dumps({'error': f'Music directory not found. Checked path: {BASE_MUSIC_DIR}'})
            self.wfile.write(error_message.encode('utf-8'))
            return

        all_file_paths = []
        for root, dirs, files in os.walk(BASE_MUSIC_DIR):
            for filename in files:
                relative_path = os.path.relpath(os.path.join(root, filename), BASE_MUSIC_DIR)
                web_path = os.path.join('/music', relative_path).replace(os.sep, '/')
                all_file_paths.append(web_path)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        json_response = json.dumps(all_file_paths)
        self.wfile.write(json_response.encode('utf-8'))
        return