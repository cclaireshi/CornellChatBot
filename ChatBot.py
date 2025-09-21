import requests
import json
import sys

# In a real application, you would load your API key securely from an environment variable.
# For this example, you can paste your API key here for testing.
API_KEY = "" 
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key="

def get_gemini_response(prompt):
    """
    Sends a prompt to the Gemini API and returns the response.
    """
    # This is the system instruction that makes the model a Cornell expert.
    # It will be sent with every request to maintain the persona.
    system_prompt = "You are a specialized AI assistant that provides information exclusively about Cornell University. Your knowledge is based on real-time, grounded data. Answer all questions concisely and professionally, as a university expert would. If you are asked about a topic unrelated to Cornell, politely decline and redirect the user to ask about Cornell University instead. If a question is too broad or cannot be answered with the available information, ask for more specific details."

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    try:
        # Make the API call
        response = requests.post(
            API_URL + API_KEY,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
        
        # Parse the JSON response
        result = response.json()
        
        # Extract text and sources from the response
        candidate = result.get("candidates", [{}])[0]
        text = "I'm sorry, I couldn't find an answer to that question. Please try asking in a different way or be more specific about Cornell University."
        sources = []

        if candidate and candidate.get("content", {}).get("parts", [{}])[0].get("text"):
            text = candidate["content"]["parts"][0]["text"]
            grounding_metadata = candidate.get("groundingMetadata", {})
            if grounding_metadata and grounding_metadata.get("groundingAttributions"):
                sources = [
                    {"uri": attr["web"]["uri"], "title": attr["web"]["title"]}
                    for attr in grounding_metadata["groundingAttributions"]
                    if attr.get("web")
                ]
        
        return text, sources

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}", file=sys.stderr)
        return "An error occurred while fetching the response. Please check your API key and network connection.", []
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}", file=sys.stderr)
        print(f"Response content: {response.text}", file=sys.stderr)
        return "An error occurred while processing the response.", []
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return "An unexpected error occurred. Please try again later.", []

if __name__ == "__main__":
    print("Welcome to the Cornell AI Assistant. Type 'exit' to quit.")
    while True:
        user_input = input("\n> ")
        if user_input.lower() == 'exit':
            break
        
        if not user_input.strip():
            print("Please enter a question.")
            continue

        print("Thinking...", end="", flush=True)
        response_text, sources = get_gemini_response(user_input)
        
        print("\n" + response_text.replace("•", "  *"))
        
        if sources:
            print("\nSources:")
            for source in sources:
                print(f"  - {source['title']} ({source['uri']})")