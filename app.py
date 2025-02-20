import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Environment variables (API keys)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# Hugging Face model
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"  # Or a suitable chat model

def search_google(query):
    """Search Google using Custom Search API with structured results and error handling."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors (4xx or 5xx)
        data = response.json()
        results = []
        if "items" in data:
            for item in data["items"][:3]:  # Limit to top 3 results
                results.append({
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", "No Link"),
                    "snippet": item.get("snippet", "No Snippet")
                })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Google Search Error: {e}")  # Log the error
        return []

def generate_ai_response(user_query, search_results):
    """Generate AI response using Hugging Face API, incorporating structured search results."""

    prompt = f"User asked: {user_query}\n\n"

    if search_results:
        prompt += "Here's some relevant information found on the web:\n"
        for i, result in enumerate(search_results):
            prompt += f"{i+1}. {result['title']}\n"
            prompt += f"   Snippet: {result['snippet']}\n"
            prompt += f"   Link: {result['link']}\n\n"
    else:
        prompt += "No relevant information found on the web.\n\n"

    prompt += "Based on this information, provide a helpful and informative answer.  Be concise and to the point." # More specific instruction

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 350, "temperature": 0.7, "top_p": 0.95}  # Adjust parameters
    }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=data,
            timeout=10 # Set a timeout for the request
        )
        response.raise_for_status() # Check for HTTP errors

        response_json = response.json()

        if isinstance(response_json, list) and len(response_json) > 0 and "generated_text" in response_json[0]:
            return response_json[0]["generated_text"].strip()  # Remove leading/trailing whitespace
        else:
            print(f"Unexpected HF response: {response_json}")  # Log
            return "Error: Could not generate a response."

    except requests.exceptions.RequestException as e:
        print(f"HF API Error: {e}")  # Log
        return f"Error generating AI response: {str(e)}"
    except (json.JSONDecodeError, KeyError, IndexError) as e: # Catch more specific errors
        print(f"Error processing HF response: {e}, Response Text: {response.text if hasattr(response, 'text') else 'No Response Text'}")
        return "Error processing the AI response."
    except Exception as e: # Catch any other error
        print(f"A general error occurred: {e}")
        return "An unexpected error occurred."


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_query = data.get("query", "")

    search_results = search_google(user_query)
    ai_response = generate_ai_response(user_query, search_results)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
