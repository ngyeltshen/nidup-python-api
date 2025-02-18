from app import app  # Import the Flask app from app.py

if __name__ != "__main__":
    application = app  # Assign Flask app to 'application' for Gunicorn
