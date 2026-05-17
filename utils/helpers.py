import os
from dotenv import load_dotenv


def get_groq_api_key():
    load_dotenv()
    return os.getenv("GROQ_API_KEY")
