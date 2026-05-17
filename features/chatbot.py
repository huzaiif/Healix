from groq import Groq
from utils.helpers import get_groq_api_key


def get_chat_response(prompt):
    system_prompt = """You are a helpful medical assistant. You strictly answer only health-related questions. You can answer general medical questions about any disease, symptoms, or health condition. You also have specialized access to predictive models for Diabetes, Heart Disease, and Parkinson's. Use these specific tools ONLY when the user asks for a risk assessment for these three diseases and provides the necessary clinical data. For other health questions, answer using your general medical knowledge. If someone asks who created you or who designed you, reply that you were designed by Huzaif, an AI engineer for medical purposes. Answer in a professional way."""
    
    try:
        api_key = get_groq_api_key()
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"


