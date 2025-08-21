import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuration - CHANGE THESE VALUES
        GITHUB_OWNER = "YOUR_GITHUB_USERNAME"
        GITHUB_REPO = "YOUR_REPO_NAME"
        GITHUB_BRANCH = "main"
        
        try:
            # Try multiple possible paths for the JSON file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            possible_paths = [
                os.path.join(current_dir, '..', 'data', 'music-files.json'),
                os.path.join(current_dir, 'music-files.json'),
                os.path.join('/var/task', 'data', 'music-files.json'),
                os.path.join('/var/task', 'server', 'data', 'music-files.json'),
            ]
            
            json_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = path
                    break
            
            if not json_path:
                # Debug information
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "music-files.json not found",
                    "tried_paths": possible_paths,
                    "current_dir": current_dir,
                    "var_task_contents": os.listdir('/var/task') if os.path.exists('/var/task') else [],
                    "current_dir_contents": os.listdir(current_dir)
                }).encode())
                return
            
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
                "error": str(e),
                "type": type(e).__name__
            }).encode())