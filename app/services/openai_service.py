import json
import openai
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Access environment variables securely
api_key = os.getenv('OPENAI_API_KEY')
organization = os.getenv('OPENAI_ORGANIZATION')

# Initialize the OpenAI client with environment variables
openai.api_key = api_key
openai.organization = organization

def load_context():
    try:
        with open('chat_context.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def ask_openai(question, messages):
    response_text = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages + [{"role": "user", "content": question}]
        )
        response_text = response['choices'][0]['message']['content']
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": response_text})
        # No longer saving the new context
        # save_context(messages)
    except openai.error.RateLimitError as e:
        response_text = "Rate limit exceeded. Please check your plan and billing details."
    except openai.error.InvalidRequestError as e:
        response_text = f"Invalid request: {str(e)}"
    except openai.error.AuthenticationError as e:
        response_text = f"Authentication error: {str(e)}. Please check your API key and organization."
    except openai.error.OpenAIError as e:
        response_text = f"An error occurred: {str(e)}"
    except Exception as e:
        response_text = f"An unexpected error occurred: {str(e)}"
    return response_text

