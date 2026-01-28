import google.generativeai as genai
import os

# The key provided by the user
KEY = "AIzaSyDFknuVa3TT-11HACm2FUXJIJRKLUCJgm0"

def test_model(model_name):
    print(f"\n--- Testing {model_name} ---")
    try:
        genai.configure(api_key=KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, simply say 'OK'.")
        print(f"✅ SUCCESS! Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ FAILED.")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print(f"Testing API Key: {KEY[:5]}...{KEY[-4:]}")
    
    # Test the problematic one
    test_model("gemini-2.0-flash")
    
    # Test the recommended one
    test_model("gemini-2.0-flash-lite-preview-02-05")
    
    # Test the confirmed reliable one
    test_model("gemini-1.5-flash")
    
