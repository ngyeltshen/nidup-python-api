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
    """Search Google using Custom Search API"""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    data = response.json()
    if "items" in data:
        return " ".join([item["snippet"] for item in data["items"][:3]])  # Extract snippets
    return "No relevant information found."

def generate_ai_response(user_query):
    """Generate response using OpenAI API"""
    search_content = search_google(user_query)  # Get relevant website content
    prompt = f"User asked: {user_query}. Based on extracted info: {search_content}, provide an answer."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
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
