import os
from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

# Get API keys from environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def search_google(query):
    # ... (Your search_google function code)

def generate_ai_response(user_query):
    # ... (Your generate_ai_response function code)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # ... (Your chatbot function code)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get port from environment
    app.run(debug=True, host='0.0.0.0', port=port) # Run on all interfaces
