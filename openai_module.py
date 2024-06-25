# openai_module.py
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Access environment variables securely
api_key = os.getenv('OPENAI_API_KEY')
organization = os.getenv('OPENAI_ORGANIZATION')
client = OpenAI(
    api_key=api_key,
    organization=organization
)

if not api_key or not organization:
    raise ValueError("API key or organization ID not set. Please check your environment variables.")

def load_context():
    try:
        with open('chat_context.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_context(messages):
    with open('chat_context.json', 'w') as file:
        json.dump(messages, file)

def ask_openai(question, messages):
    response_text = ""
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages + [{"role": "user", "content": question}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content
    messages.append({"role": "user", "content": question})
    messages.append({"role": "assistant", "content": response_text})
    save_context(messages)
    return response_text
