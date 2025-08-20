# server/api/index.py
import os
import json
from flask import Flask, Response, abort, request
from pathlib import PurePosixPath

app = Flask(__name__)

# --- Routes ---

@app.route('/music', strict_slashes=False)
def browse_music():
    path = request.args.get('path', os.getcwd())
    return Response(os.listdir(path).append(os.getcwd()).__str__())
    

@app.route('/', strict_slashes=False)
def hello_world():
    return 'Hello, World! Try navigating to <a href="/music">/music</a>.'
