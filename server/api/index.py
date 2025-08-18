from flask import Flask
import os

app = Flask(__name__)

# Add strict_slashes=False to make the trailing slash optional
@app.route('/', strict_slashes=False)
def hello_world():
    return os.listdir("../..")

@app.route('/about', strict_slashes=False)
def about_page():
    return 'This is the About Page.'