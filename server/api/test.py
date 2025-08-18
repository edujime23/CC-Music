from flask import Flask

app = Flask(__name__)

# Add strict_slashes=False to make the trailing slash optional
@app.route('/', strict_slashes=False)
def hello_world():
    return 'Hello, World!'

@app.route('/about', strict_slashes=False)
def about_page():
    return 'This is the About Page.'