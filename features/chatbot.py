import os
from google import genai
from google.genai import types
from utils.helpers import get_google_api_key

def init_chatbot():
    api_key = get_google_api_key()
    if not api_key:
        return False
    return True

def get_chat_response(prompt):
    system_prompt = """You are a helpful medical assistant. You strictly answer only health-related questions. You can answer general medical questions about any disease, symptoms, or health condition. You also have specialized access to predictive models for Diabetes, Heart Disease, and Parkinson's. Use these specific tools ONLY when the user asks for a risk assessment for these three diseases and provides the necessary clinical data. For other health questions, answer using your general medical knowledge. If someone asks who created you or who designed you, reply that you were designed by Huzaif, an AI engineer for medical purposes. Answer in a professional way."""
    
    try:
        api_key = get_google_api_key()
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

def generate_health_tips(diagnosis, disease_name):
    init_chatbot()
    try:
        system_prompt = """You are a helpful medical assistant. You strictly answer only health-related questions. You can answer general medical questions about any disease, symptoms, or health condition."""
        prompt = f"The user has been diagnosed with the following result for {disease_name}: {diagnosis}. Please provide 3-5 short, actionable, and professional health tips or advice relevant to this specific result. Start with a reassuring tone."
        
        api_key = get_google_api_key()
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text
    except Exception as e:
        return f"Could not generate health tips due to an error: {e}"
