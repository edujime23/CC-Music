# server/api/index.py
import os
import json
from flask import Flask, Response, abort
from pathlib import PurePosixPath

app = Flask(__name__)

# --- Data Loading and Tree Building ---

MUSIC_TREE = {}
MANIFEST_FILE = os.path.join(os.path.dirname(__file__), 'music_files.json')

def build_music_tree():
    """Reads the JSON manifest and builds a nested dictionary representing the file structure."""
    if not os.path.exists(MANIFEST_FILE):
        raise RuntimeError("Music manifest file not found. Run the build script.")

    with open(MANIFEST_FILE, 'r') as f:
        data = json.load(f)

    tree = {'_dirs': {}, '_files': {}}
    for item in data['files']:
        path = PurePosixPath(item['path'])
        current_level = tree
        # Iterate through path parts (e.g., 'music', 'a', 'b')
        for part in path.parts[1:-1]: # Skip root '/' and the filename
            if part not in current_level['_dirs']:
                current_level['_dirs'][part] = {'_dirs': {}, '_files': {}}
            current_level = current_level['_dirs'][part]
        # Add the file to the final directory
        current_level['_files'][path.name] = item['raw_url']
    
    return tree

# Build the tree once when the application starts
try:
    MUSIC_TREE = build_music_tree()
except RuntimeError as e:
    print(e)


# --- HTML Template ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Index of {path}</title>
    <style>
        body {{ font-family: monospace; padding: 20px; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ padding: 5px 0; }}
        a {{ text-decoration: none; color: #007bff; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Index of {path}</h1>
    <hr>
    <ul>
        <li><a href="{parent_path}">[../] Parent Directory</a></li>
        {directories}
        {files}
    </ul>
    <hr>
</body>
</html>
"""

# --- Routes ---

@app.route('/music/', defaults={'subpath': ''}, strict_slashes=False)
@app.route('/music/<path:subpath>', strict_slashes=False)
def browse_music(subpath):
    """Navigates the MUSIC_TREE and displays the contents of a directory."""
    
    current_level = MUSIC_TREE
    path_parts = [p for p in subpath.split('/') if p]

    # Navigate the tree based on the subpath
    for part in path_parts:
        if part in current_level['_dirs']:
            current_level = current_level['_dirs'][part]
        else:
            abort(404, "Directory not found")

    # Prepare parent directory link
    current_path = f"/music/{subpath}"
    parent_path = os.path.dirname(current_path.strip('/'))
    if not parent_path:
        parent_path = "/music"
    else:
        parent_path = f"/{parent_path}"


    # Generate HTML for subdirectories
    dir_html = ""
    for dirname in sorted(current_level['_dirs'].keys()):
        dir_html += f'<li><a href="{current_path.rstrip("/")}/{dirname}/">{dirname}/</a></li>'

    # Generate HTML for files
    file_html = ""
    for filename, raw_url in sorted(current_level['_files'].items()):
        file_html += f'<li><a href="{raw_url}" target="_blank">{filename}</a></li>'

    # Render the final HTML
    html_content = HTML_TEMPLATE.format(
        path=current_path,
        parent_path=parent_path,
        directories=dir_html,
        files=file_html
    )
    return Response(html_content, mimetype='text/html')


@app.route('/', strict_slashes=False)
def hello_world():
    return 'Hello, World! Try navigating to <a href="/music">/music</a>.'
