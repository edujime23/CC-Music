# server/api/index.py

import os
import json
from flask import Flask, jsonify

app = Flask(__name__)

# --- This is the new part ---

# Define the path to the manifest file created by the build script.
# __file__ is the path to the current script (index.py).
# This makes sure we can always find the JSON file, as it's in the same 'api' directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(script_dir, 'music_files.json')

@app.route('/music', strict_slashes=False)
def get_music_list():
    """
    Reads the pre-generated JSON manifest and returns the list of music files.
    """
    try:
        # Check if the manifest file actually exists
        if not os.path.exists(MANIFEST_FILE):
            # If not, return a 404 Not Found error
            return jsonify({"error": "Music manifest file not found. Please check the build logs."}), 404

        # Open the file, load the JSON data, and return it
        with open(MANIFEST_FILE, 'r') as f:
            data = json.load(f)
        
        # jsonify() correctly sets the Content-Type header to application/json
        return jsonify(data)

    except Exception as e:
        # Return a generic 500 error if anything else goes wrong
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

# --- Your existing routes ---

# Add strict_slashes=False to make the trailing slash optional
@app.route('/', strict_slashes=False)
def hello_world():
    return 'Hello, World!'

@app.route('/about', strict_slashes=False)
def about_page():
    return 'This is the About Page.'
