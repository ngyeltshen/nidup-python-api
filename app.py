import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Environment variables (API keys)
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# Hugging Face model
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"  # Or a suitable chat model

def generate_ai_response(user_query):
    """Generate AI response using Hugging Face API."""
    prompt = user_query  # Removed unnecessary formatting to avoid repeating the query

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
            timeout=10  # Set a timeout for the request
        )
        response.raise_for_status()  # Check for HTTP errors

        response_json = response.json()

        if isinstance(response_json, list) and len(response_json) > 0 and "generated_text" in response_json[0]:
            return response_json[0]["generated_text"].strip()  # Remove leading/trailing whitespace
        else:
            print(f"Unexpected HF response: {response_json}")  # Log
            return "Error: Could not generate a response."

    except requests.exceptions.RequestException as e:
        print(f"HF API Error: {e}")  # Log
        return f"Error generating AI response: {str(e)}"
    except (json.JSONDecodeError, KeyError, IndexError) as e:  # Catch more specific errors
        print(f"Error processing HF response: {e}, Response Text: {response.text if hasattr(response, 'text') else 'No Response Text'}")
        return "Error processing the AI response."
    except Exception as e:  # Catch any other error
        print(f"A general error occurred: {e}")
        return "An unexpected error occurred."


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_query = data.get("query", "")
    ai_response = generate_ai_response(user_query)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

