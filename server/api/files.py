import json
from http.server import BaseHTTPRequestHandler

try:
    from music_data import MUSIC_FILES
except ImportError:
    # Fallback if music_data.py doesn't exist
    MUSIC_FILES = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuration - CHANGE THESE VALUES
        GITHUB_OWNER = "YOUR_GITHUB_USERNAME"  # Change this!
        GITHUB_REPO = "YOUR_REPO_NAME"  # Change this!
        GITHUB_BRANCH = "main"  # Change if needed
        
        try:
            # Add GitHub raw URLs to each file
            files_with_urls = []
            for file in MUSIC_FILES:
                file_with_url = file.copy()
                file_with_url['raw_url'] = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/music/{file['path']}"
                files_with_urls.append(file_with_url)
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
            self.end_headers()
            
            response_data = {
                "files": files_with_urls,
                "total": len(files_with_urls)
            }
            
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_data = {
                "error": str(e),
                "type": type(e).__name__
            }
            
            self.wfile.write(json.dumps(error_data).encode())