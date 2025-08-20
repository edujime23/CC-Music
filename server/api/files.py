# In file: api/files.py
import os
import json
from http.server import BaseHTTPRequestHandler

# Define paths for clarity and debugging
SCRIPT_DIR = os.path.dirname(__file__) # The directory the script is in (e.g., /var/task/api)
PROJECT_ROOT_GUESS = os.path.abspath(os.path.join(SCRIPT_DIR, '..')) # The parent dir (e.g., /var/task)
BASE_MUSIC_DIR = os.path.join(PROJECT_ROOT_GUESS, 'music')

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # If the directory doesn't exist, we send back rich debug info
        if not os.path.isdir(BASE_MUSIC_DIR):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Try to get directory listings for debugging
            try:
                project_root_contents = os.listdir(PROJECT_ROOT_GUESS)
            except Exception as e:
                project_root_contents = f"Error listing project root guess: {e}"

            # Construct the detailed debug payload
            debug_info = {
                "error": "Music directory not found on server.",
                "path_we_checked_for_music": BASE_MUSIC_DIR,
                "project_root_we_checked": PROJECT_ROOT_GUESS,
                "what_is_in_the_project_root": project_root_contents,
                "current_working_directory": os.getcwd()
            }
            
            response_body = json.dumps(debug_info, indent=2)
            self.wfile.write(response_body.encode('utf-8'))
            return

        # --- If the directory exists, proceed as normal ---
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