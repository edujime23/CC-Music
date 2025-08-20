# server/api/index.py
import os
import json
from flask import Flask, Response, abort
from pathlib import PurePosixPath

app = Flask(__name__)

# --- Routes ---

@app.route('/music/', defaults={'subpath': ''}, strict_slashes=False)
@app.route('/music/<path:subpath>', strict_slashes=False)
def browse_music(subpath):
    if subpath:
        return os.listdir(subpath)
    

@app.route('/', strict_slashes=False)
def hello_world():
    return 'Hello, World! Try navigating to <a href="/music">/music</a>.'
