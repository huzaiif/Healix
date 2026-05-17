import json
from groq import Groq
from utils.helpers import get_groq_api_key


def generate_ml_structured_report(disease_name, patient_info, ml_inputs, diagnosis_result):
    api_key = get_groq_api_key()
    if not api_key:
        return None
        
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
    
    system_prompt = f"""You are a professional medical AI assistant. Analyze the following ML Model diagnosis and inputs, and return the output STRICTLY in the following JSON format.
    
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
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        
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
