import google.generativeai as genai
import os

# usage: python check_models.py

api_key = "AIzaSyAaMQcLQS009cpvXkM1fX3hyf-zsk4jTCM"

try:
    genai.configure(api_key=api_key)
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
