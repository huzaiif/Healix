import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "health_gpt.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(username, email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                       (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def save_chat(user_id, message, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, message, role) VALUES (?, ?, ?)",
                   (user_id, message, role))
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    chats = cursor.fetchall()
    conn.close()
    return [dict(row) for row in chats]

def clear_chat_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def save_health_record(user_id, age, weight, height, medical_conditions, allergies):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if a record already exists
    cursor.execute("SELECT id FROM health_records WHERE user_id = ?", (user_id,))
    record = cursor.fetchone()
    
    if record:
        cursor.execute("""
            UPDATE health_records 
            SET age = ?, weight = ?, height = ?, medical_conditions = ?, allergies = ?
            WHERE user_id = ?
        """, (age, weight, height, medical_conditions, allergies, user_id))
    else:
        cursor.execute("""
            INSERT INTO health_records (user_id, age, weight, height, medical_conditions, allergies) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, age, weight, height, medical_conditions, allergies))
        
    conn.commit()
    conn.close()

def get_health_record(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_records WHERE user_id = ?", (user_id,))
    record = cursor.fetchone()
    conn.close()
    return dict(record) if record else None

def save_recommendation(user_id, recommendation_text, recommendation_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recommendation_history (user_id, recommendation_text, recommendation_type)
        VALUES (?, ?, ?)
    """, (user_id, recommendation_text, recommendation_type))
    conn.commit()
    conn.close()

def get_recommendations(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendation_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    recs = cursor.fetchall()
    conn.close()
    return [dict(row) for row in recs]

def save_report(user_id, title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO saved_reports (user_id, title, content) VALUES (?, ?, ?)",
                   (user_id, title, content))
    conn.commit()
    conn.close()

def get_reports(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    reports = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reports]

def delete_report(report_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_reports WHERE id = ? AND user_id = ?", (report_id, user_id))
    conn.commit()
    conn.close()

def save_vitals_record(user_id, hr, temp, spo2, sys_bp, dia_bp, symptoms, risk_level, report_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vitals_history 
        (user_id, heart_rate, temperature, spo2, sys_bp, dia_bp, symptoms, ai_risk_level, report_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, hr, temp, spo2, sys_bp, dia_bp, symptoms, risk_level, report_id))
    conn.commit()
    conn.close()

def get_vitals_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vitals_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]
