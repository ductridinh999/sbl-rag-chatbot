import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: 'GOOGLE_API_KEY' not found. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

    print("Key configured from .env. Checking available models...")

    try:
        found_flash = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                if "gemini-2.0-flash" in m.name:
                    found_flash = True

        print("\n------------------------------------------------")
        if found_flash:
            print("SUCCESS: You have access to 'gemini-2.0-flash'!")
            print("Model name: gemini-2.0-flash")
        else:
            print("'gemini-2.0-flash' wasn't listed.")
            
    except Exception as e:
        print(f"Error: Your key might be invalid or there is a connection issue. Details:\n{e}")