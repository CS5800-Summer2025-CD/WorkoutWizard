# Import the Flask class and render_template function from the flask module
from flask import Flask, render_template

# Create an instance of the Flask class.
# The __name__ argument tells Flask where to look for resources.
app = Flask(__name__)

# Define a route for the home page ('/')
# When a user navigates to the root URL of your app, this function will be executed.
@app.route('/')
def hello_world():
    """
    This function renders an HTML template named 'index.html'.
    This HTML content will be displayed in the user's web browser.
    """
    # The render_template function looks for templates in a 'templates' folder
    # by default, relative to the application's root directory.
    return render_template('index.html')

# This block ensures that the Flask development server runs only when the script
# is executed directly (not when it's imported as a module into another script).
if __name__ == '__main__':
    # Run the Flask application in debug mode.
    # Debug mode provides helpful error messages in the browser and
    # automatically reloads the server when code changes are detected.
    app.run(debug=True)