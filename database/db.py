import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables")
        return None
    return create_client(url, key)

supabase = get_supabase()

def create_chat_session(user_id, title="New Chat"):
    try:
        response = supabase.table('chat_sessions').insert({
            "user_id": user_id,
            "title": title
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating chat session: {e}")
        return None

def get_chat_sessions(user_id):
    try:
        response = supabase.table('chat_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting chat sessions: {e}")
        return []

def delete_chat_session(session_id, user_id):
    try:
        supabase.table('chat_sessions').delete().eq('id', session_id).eq('user_id', user_id).execute()
    except Exception as e:
        print(f"Error deleting chat session: {e}")

def save_chat(user_id, session_id, message, role):
    try:
        supabase.table('chat_history').insert({
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "role": role
        }).execute()
    except Exception as e:
        print(f"Error saving chat: {e}")

def get_chat_history(user_id, session_id=None):
    try:
        query = supabase.table('chat_history').select('*').eq('user_id', user_id)
        if session_id:
            query = query.eq('session_id', session_id)
        response = query.order('timestamp', desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def clear_chat_history(user_id, session_id=None):
    try:
        query = supabase.table('chat_history').delete().eq('user_id', user_id)
        if session_id:
            query = query.eq('session_id', session_id)
        query.execute()
    except Exception as e:
        print(f"Error clearing chat history: {e}")

def save_health_record(user_id, age, weight, height, medical_conditions, allergies):
    try:
        response = supabase.table('health_records').select('id').eq('user_id', user_id).execute()
        if response.data:
            supabase.table('health_records').update({
                "age": age,
                "weight": weight,
                "height": height,
                "medical_conditions": medical_conditions,
                "allergies": allergies
            }).eq('user_id', user_id).execute()
        else:
            supabase.table('health_records').insert({
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "height": height,
                "medical_conditions": medical_conditions,
                "allergies": allergies
            }).execute()
    except Exception as e:
        print(f"Error saving health record: {e}")

def get_health_record(user_id):
    try:
        response = supabase.table('health_records').select('*').eq('user_id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting health record: {e}")
        return None

def save_recommendation(user_id, recommendation_text, recommendation_type):
    try:
        supabase.table('recommendation_history').insert({
            "user_id": user_id,
            "recommendation_text": recommendation_text,
            "recommendation_type": recommendation_type
        }).execute()
    except Exception as e:
        print(f"Error saving recommendation: {e}")

def get_recommendations(user_id):
    try:
        response = supabase.table('recommendation_history').select('*').eq('user_id', user_id).order('timestamp', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

def save_report(user_id, title, content):
    try:
        supabase.table('saved_reports').insert({
            "user_id": user_id,
            "title": title,
            "content": content
        }).execute()
    except Exception as e:
        print(f"Error saving report: {e}")

def get_reports(user_id):
    try:
        response = supabase.table('saved_reports').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting reports: {e}")
        return []

def get_report_by_id(report_id, user_id):
    try:
        response = supabase.table('saved_reports').select('*').eq('id', report_id).eq('user_id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting report by id: {e}")
        return None

def save_assessment_metrics(user_id, disease, metrics_json, is_positive):
    try:
        supabase.table('assessment_metrics').insert({
            "user_id": user_id,
            "disease": disease,
            "metrics": json.dumps(metrics_json) if isinstance(metrics_json, dict) else metrics_json,
            "is_positive": int(is_positive)
        }).execute()
    except Exception as e:
        print(f"Error saving assessment metrics: {e}")

def get_assessment_metrics(user_id, disease=None):
    try:
        query = supabase.table('assessment_metrics').select('*').eq('user_id', user_id)
        if disease:
            query = query.eq('disease', disease)
        response = query.order('timestamp', desc=False).execute()
        
        result = []
        for row in response.data:
            try:
                row['metrics'] = json.loads(row['metrics'])
            except Exception:
                row['metrics'] = {}
            result.append(row)
        return result
    except Exception as e:
        print(f"Error getting assessment metrics: {e}")
        return []
