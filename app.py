# Import the core Flask class
from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Define the root route (home page)
@app.route('/')
def home():
    # Return a simple response for the home page
    return "Hello, My Tech Blog! 🚀 This is my first Flask web service."

# Run the application if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)  # debug=True: auto-restart when code changesgi