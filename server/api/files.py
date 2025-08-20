import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuration - CHANGE THESE VALUES
        GITHUB_OWNER = "edujime23"
        GITHUB_REPO = "CC-Music"
        GITHUB_BRANCH = "main"
        
        try:
            # Load pre-generated file list
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, '..', 'data', 'music-files.json')
            
            with open(json_path, 'r') as f:
                files = json.load(f)
            
            # Add GitHub raw URLs
            for file in files:
                file['raw_url'] = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/music/{file['path']}"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "files": files,
                "total": len(files)
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode())