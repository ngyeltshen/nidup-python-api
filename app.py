import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

#enable CORS
CORS(app)

# Get API keys from environment variables
GOOGLE_API_KEY = os.environ.get("AIzaSyA8g5TvktDzf86ITyd0Cz7hwTsKebUjTtY")
SEARCH_ENGINE_ID = os.environ.get("101ec59658da64424")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")  # Hugging Face API key

# Hugging Face model
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

def search_google(query):
    """Search Google using Custom Search API"""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    data = response.json()
    if "items" in data:
        return " ".join([item["snippet"] for item in data["items"][:3]])  # Extract snippets
    return "No relevant information found."

def generate_ai_response(user_query):
    """Generate response using Hugging Face API"""
    search_content = search_google(user_query)  # Get relevant website content
    #prompt = f"User asked: {user_query}. Based on extracted info: {search_content}, provide an answer."
   prompt = f"{search_content}"


    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200}  # Limit tokens to keep responses concise
    }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=data
        )
        response_json = response.json()

        if "error" in response_json:
            return f"Error from Hugging Face API: {response_json['error']}"

        return response_json[0]["generated_text"]  # Extract generated text

    except Exception as e:
        return f"Error generating AI response: {str(e)}"

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot requests"""
    data = request.get_json()
    user_query = data.get("query", "")
    ai_response = generate_ai_response(user_query)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get port from environment
    app.run(debug=True, host='0.0.0.0', port=port)  # Run Flask server on all interfaces
  
