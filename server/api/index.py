from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)

# --- Data Loading and Caching ---
# We build the file tree once when the application starts.
# This is much more efficient than reading the file on every request.

def build_file_tree_from_manifest():
    """Reads the flat file list and builds a nested dictionary representing the directory structure."""
    try:
        current_dir = Path(__file__).parent
        manifest_path = current_dir / 'file_manifest.txt'
        
        with open(manifest_path, 'r') as f:
            paths = [line.strip() for line in f.readlines() if line.strip()]

        file_tree = {}
        for path in paths:
            parts = path.split('/')
            current_level = file_tree
            for part in parts[:-1]: # Iterate through directories
                # setdefault is a clever way to create a key if it doesn't exist
                current_level = current_level.setdefault(part, {})
            # The last part is the file
            current_level[parts[-1]] = True # Mark as a file
        
        return file_tree

    except FileNotFoundError:
        # If the manifest is missing, the app can't work. Return an error structure.
        return {"error": "file_manifest.txt not found. Check Vercel build command."}

# This is our cached, in-memory representation of the file system.
FILE_TREE = build_file_tree_from_manifest()

# --- API Routes ---

@app.route('/')
def home():
    """Provides instructions on how to use the API."""
    return jsonify({
        "message": "Welcome to the file browser API!",
        "usage": "Navigate to /browse/ to see the root directory, or /browse/path/to/dir/ to see subdirectories."
    })

@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    """Navigates the file tree and returns the contents of a directory."""
    if "error" in FILE_TREE:
        return jsonify(FILE_TREE), 500

    current_level = FILE_TREE
    path_parts = [part for part in subpath.split('/') if part] # Clean up empty parts

    # Traverse the tree to find the requested directory
    try:
        for part in path_parts:
            current_level = current_level[part]
    except (KeyError, TypeError):
        return jsonify({"error": f"Path not found: '{subpath}'"}), 404

    # Once at the correct level, list the contents
    directories = []
    files = []
    
    if not isinstance(current_level, dict):
         return jsonify({"error": f"Path points to a file, not a directory: '{subpath}'"}), 400

    for name, content in current_level.items():
        if isinstance(content, dict): # If the value is a dictionary, it's a directory
            directories.append(name)
        else: # Otherwise, it's a file
            files.append(name)
            
    return jsonify({
        "path": f"/{subpath}",
        "directories": sorted(directories),
        "files": sorted(files)
    })
