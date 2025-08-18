from flask import Flask, jsonify
import os
from pathlib import Path

app = Flask(__name__)

# This function will load the file list from our manifest
def get_music_file_list():
    # The Python script is in /api/, so the manifest is one level up.
    # Using pathlib is the most reliable way to handle paths.
    current_dir = Path(__file__).parent
    manifest_path = current_dir.parent / 'file_manifest.txt'
    
    try:
        with open(manifest_path, 'r') as f:
            # Read all lines, and strip any whitespace/newlines from each line
            files = [line.strip() for line in f.readlines()]
        return files
    except FileNotFoundError:
        # This error will show up if the build command failed for some reason
        return ["Error: file_manifest.txt not found. Check the Vercel build command."]


@app.route('/', strict_slashes=False)
def hello_world():
    # Get the deep list of files from our pre-built manifest
    file_list = get_music_file_list()
    
    # Returning as JSON is best practice for an API
    return jsonify(file_list)


@app.route('/about', strict_slashes=False)
def about_page():
    return 'This is the About Page.'
