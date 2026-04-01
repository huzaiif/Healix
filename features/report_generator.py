import json
import google.generativeai as genai
from utils.helpers import get_google_api_key

def generate_structured_report(patient_info, vitals, symptoms):
    api_key = get_google_api_key()
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    
    schema = """
    {
        "ai_analysis": {
            "summary": "Brief summary of the condition",
            "risk_level": "Low | Moderate | High",
            "probable_conditions": ["Condition 1", "Condition 2"]
        },
        "recommendations": {
            "immediate_actions": ["Action 1"],
            "lifestyle_suggestions": ["Suggestion 1"],
            "monitoring_advice": ["Monitoring 1"]
        },
        "emergency_flags": {
            "critical_symptoms_to_watch": ["Symptom 1"],
            "seek_immediate_care_if": "Condition description"
        }
    }
    """
    
    system_prompt = f"""You are a professional medical AI assistant. Analyze the following patient data and return the output STRICTLY in the following JSON format. Do not add markdown formatting or backticks like ```json.
    
    Required JSON Schema:
    {schema}
    """
    
    prompt = f"""
    Patient Age: {patient_info.get('age', 'N/A')}, Gender: {patient_info.get('gender', 'N/A')}
    Vitals: HR {vitals.get('heart_rate')} bpm, Temp {vitals.get('temperature')}F, SpO2 {vitals.get('spo2')}%, BP {vitals.get('sys_bp')}/{vitals.get('dia_bp')} mmHg
    Symptoms: {symptoms}
    """
    
    try:
        model = genai.GenerativeModel("gemini-flash-lite-latest", system_instruction=system_prompt)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        
        # Combine everything into the final format
        report_data = {
            "patient_info": patient_info,
            "vitals": vitals,
            "symptoms": symptoms,
            "ai_analysis": data.get("ai_analysis", {}),
            "recommendations": data.get("recommendations", {}),
            "emergency_flags": data.get("emergency_flags", {})
        }
        return report_data
        
    except Exception as e:
        print(f"Error generating structured report: {e}")
        return None

def generate_ml_structured_report(disease_name, patient_info, ml_inputs, diagnosis_result):
    api_key = get_google_api_key()
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    
    schema = """
    {
        "ai_analysis": {
            "summary": "Brief summary of the condition",
            "risk_level": "Low | Moderate | High",
            "probable_conditions": ["Condition 1", "Condition 2"]
        },
        "recommendations": {
            "immediate_actions": ["Action 1"],
            "lifestyle_suggestions": ["Suggestion 1"],
            "monitoring_advice": ["Monitoring 1"]
        },
        "emergency_flags": {
            "critical_symptoms_to_watch": ["Symptom 1"],
            "seek_immediate_care_if": "Condition description"
        }
    }
    """
    
    system_prompt = f"""You are a professional medical AI assistant. Analyze the following ML Model diagnosis and inputs, and return the output STRICTLY in the following JSON format. Do not add markdown formatting or backticks like ```json.
    
    Required JSON Schema:
    {schema}
    """
    
    prompt = f"""
    Patient Age: {patient_info.get('age', 'N/A')}, Gender: {patient_info.get('gender', 'N/A')}
    Disease Evaluated: {disease_name}
    Model Diagnosis: {diagnosis_result}
    Model Inputs Used: {ml_inputs}
    """
    
    try:
        model = genai.GenerativeModel("gemini-flash-lite-latest", system_instruction=system_prompt)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        
        # Build fake vitals mapping so PDF Generator doesn't error while checking for keys
        vitals = {}
        if "Blood Pressure" in ml_inputs: vitals["sys_bp"] = ml_inputs["Blood Pressure"]
        if "trestbps" in ml_inputs: vitals["sys_bp"] = ml_inputs["trestbps"]
        if "Heart Rate" in ml_inputs or "thalach" in ml_inputs: vitals["heart_rate"] = ml_inputs.get("Heart Rate", ml_inputs.get("thalach"))
        
        report_data = {
            "patient_info": patient_info,
            "vitals": vitals,
            "symptoms": f"Evaluated for {disease_name}. ML Diagnosis result: {diagnosis_result}",
            "ai_analysis": data.get("ai_analysis", {}),
            "recommendations": data.get("recommendations", {}),
            "emergency_flags": data.get("emergency_flags", {})
        }
        return report_data
        
    except Exception as e:
        print(f"Error generating ml structured report: {e}")
        return None
