from flask import Flask

# Vercel (and other platforms) will look for an object named 'app'.
app = Flask(__name__)

# This is a "decorator" that tells Flask:
# When someone visits the main URL ('/'), run the function below.
@app.route('/')
def hello_world():
    # The string returned by this function is what the user will see in their browser.
    return 'Hello, World!'

# You can add more routes for different pages
@app.route('/about')
def about_page():
    return 'This is the About Page.'

# Note: The 'if __name__ == "__main__":' block for running locally
# is NOT needed for Vercel deployment, as Vercel handles running the app itself.