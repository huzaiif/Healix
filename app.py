import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from database.db import (supabase, get_reports, get_recommendations, save_chat,
                         get_chat_history, clear_chat_history, get_health_record, save_health_record,
                         save_assessment_metrics, get_assessment_metrics,
                         create_chat_session, get_chat_sessions, delete_chat_session)
from features.chatbot import get_chat_response
from features.recommendation import predict_diabetes, predict_heart_disease, predict_parkinsons
from features.report_generator import generate_ml_structured_report

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")



# Helper decorator for login required
def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first", "danger")
            return redirect(url_for('login'))
    wrap.__name__ = f.__name__
    return wrap

@app.route("/")
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['logged_in'] = True
            session['username'] = response.user.user_metadata.get('username', email)
            session['user_id'] = response.user.id
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash("Invalid Email or Password", "danger")
            
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    }
                }
            })
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), "danger")
            
    return render_template("register.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        try:
            # Note: For this redirect_to to work, it MUST be whitelisted in Supabase Dashboard -> Auth -> URL Configuration -> Redirect URLs
            redirect_url = url_for('reset_password', _external=True)
            supabase.auth.reset_password_email(email, options={"redirect_to": redirect_url})
            flash("If an account exists with that email, a password reset link has been sent.", "success")
        except Exception as e:
            flash(f"Error sending reset email: {e}", "danger")
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    # If Supabase redirected here with a PKCE code, exchange it for a session
    code = request.args.get("code")
    if code:
        try:
            supabase.auth.exchange_code_for_session({"auth_code": code})
        except Exception as e:
            flash(f"Error exchanging auth code: {e}", "danger")
            
    # If the JS snippet converted a fragment to query params, set the session manually
    access_token = request.args.get("access_token")
    refresh_token = request.args.get("refresh_token")
    if access_token and refresh_token:
        try:
            supabase.auth.set_session(access_token, refresh_token)
        except Exception as e:
            flash(f"Error setting session from token: {e}", "danger")

    if request.method == "POST":
        new_password = request.form.get("password")
        try:
            # We must be authenticated to update the password.
            # The exchange_code_for_session or set_session above should have authenticated us.
            supabase.auth.update_user({"password": new_password})
            flash("Password updated successfully! Please log in with your new password.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error updating password: {e}. You may need to request a new link.", "danger")
            
    return render_template("reset_password.html")

@app.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    session.clear()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    import json
    user_id = session['user_id']
    reports = get_reports(user_id)
    recommendations = get_recommendations(user_id)

    def build_chart_data(disease, metric_keys):
        """Return {labels, datasets: [{label, data}], results} for Chart.js."""
        rows = get_assessment_metrics(user_id, disease)
        labels = [r['timestamp'][:16].replace('T', ' ') for r in rows]
        datasets = []
        for key in metric_keys:
            datasets.append({
                'label': key,
                'data': [r['metrics'].get(key, 0) for r in rows]
            })
        results = [r['is_positive'] for r in rows]
        return {'labels': labels, 'datasets': datasets, 'results': results}

    diabetes_chart = build_chart_data('diabetes', ['Glucose', 'BMI', 'Blood Pressure'])
    heart_chart    = build_chart_data('heart',    ['Cholesterol', 'Max Heart Rate', 'Resting BP'])
    parkinsons_chart = build_chart_data('parkinsons', ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'HNR'])

    return render_template(
        "dashboard.html",
        username=session['username'],
        reports_count=len(reports),
        recs_count=len(recommendations),
        diabetes_chart=json.dumps(diabetes_chart),
        heart_chart=json.dumps(heart_chart),
        parkinsons_chart=json.dumps(parkinsons_chart)
    )

@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html")

@app.route("/api/chat/sessions", methods=["GET"])
@login_required
def api_chat_sessions():
    user_id = session['user_id']
    sessions = get_chat_sessions(user_id)
    return jsonify(sessions)

@app.route("/api/chat/sessions/<session_id>", methods=["DELETE"])
@login_required
def api_delete_chat_session(session_id):
    user_id = session['user_id']
    delete_chat_session(session_id, user_id)
    return jsonify({"status": "success"})

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.json
    prompt = data.get("prompt")
    session_id = data.get("session_id")
    user_id = session['user_id']
    
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400
        
    if not session_id:
        # Create a new session with a title derived from the prompt
        title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        new_session = create_chat_session(user_id, title)
        if new_session:
            session_id = new_session.get("id")
        
    save_chat(user_id, session_id, prompt, "user")
    
    # Get response
    response_text = get_chat_response(prompt)
    save_chat(user_id, session_id, response_text, "assistant")
    
    return jsonify({"response": response_text, "session_id": session_id})

@app.route("/api/chat/history", methods=["GET"])
@login_required
def api_chat_history():
    user_id = session['user_id']
    session_id = request.args.get("session_id")
    history = get_chat_history(user_id, session_id)
    return jsonify(history)

@app.route("/api/chat/clear", methods=["POST"])
@login_required
def api_chat_clear():
    user_id = session['user_id']
    session_id = request.json.get("session_id") if request.json else None
    clear_chat_history(user_id, session_id)
    return jsonify({"status": "success"})

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session['user_id']
    if request.method == "POST":
        age = request.form.get("age")
        weight = request.form.get("weight")
        height = request.form.get("height")
        conditions = request.form.get("conditions")
        allergies = request.form.get("allergies")
        save_health_record(user_id, age, weight, height, conditions, allergies)
        flash("Health profile updated successfully!", "success")
        return redirect(url_for('profile'))
        
    record = get_health_record(user_id) or {}
    return render_template("profile.html", record=record)


@app.route("/assessments", methods=["GET", "POST"])
@login_required
def assessments():
    user_id = session['user_id']
    result = None
    report_data = None
    active_tab = "diabetes"
    
    if request.method == "POST":
        assessment_type = request.form.get("assessment_type")
        patient_info = {"patient_id": f"PT-{str(user_id)[:8]}", "age": "Unknown", "gender": "Unknown"}
        
        if assessment_type == "diabetes":
            active_tab = "diabetes"
            try:
                pregnancies = float(request.form.get('pregnancies', 0))
                glucose = float(request.form.get('glucose', 0))
                blood_pressure = float(request.form.get('blood_pressure', 0))
                skin_thickness = float(request.form.get('skin_thickness', 0))
                insulin = float(request.form.get('insulin', 0))
                bmi = float(request.form.get('bmi', 0))
                dpf = float(request.form.get('dpf', 0))
                age = float(request.form.get('age', 0))
                
                user_input = [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]
                prediction = predict_diabetes(user_input)
                
                if prediction == 1:
                    diagnosis = "The person is diabetic"
                else:
                    diagnosis = "The person is not diabetic"
                    
                from database.db import save_recommendation, save_report
                save_recommendation(user_id, diagnosis, "Diabetes Assessment")
                
                inputs_dict = {
                    "Pregnancies": pregnancies, "Glucose": glucose, "Blood Pressure": blood_pressure,
                    "Skin Thickness": skin_thickness, "Insulin": insulin, "BMI": bmi,
                    "Diabetes Pedigree Function": dpf, "Age": age
                }
                
                report_data = generate_ml_structured_report("Diabetes", patient_info, inputs_dict, diagnosis)
                if report_data:
                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nGlucose: {glucose}, BMI: {bmi}, Age: {age}"
                    save_report(user_id, "Diabetes Risk Assessment", report_content)

                # Save metrics for dashboard graphs
                save_assessment_metrics(user_id, 'diabetes', {
                    'Glucose': glucose, 'BMI': bmi, 'Blood Pressure': blood_pressure,
                    'Insulin': insulin, 'Age': age
                }, prediction == 1)

                result = {"diagnosis": diagnosis, "is_positive": prediction == 1}
            except Exception as e:
                flash(f"Error processing diabetes assessment: {e}", "danger")
                
        elif assessment_type == "heart":
            active_tab = "heart"
            try:
                age = float(request.form.get('age', 0))
                sex = float(request.form.get('sex', 0))
                cp = float(request.form.get('cp', 0))
                trestbps = float(request.form.get('trestbps', 0))
                chol = float(request.form.get('chol', 0))
                fbs = float(request.form.get('fbs', 0))
                restecg = float(request.form.get('restecg', 0))
                thalach = float(request.form.get('thalach', 0))
                exang = float(request.form.get('exang', 0))
                oldpeak = float(request.form.get('oldpeak', 0))
                slope = float(request.form.get('slope', 0))
                ca = float(request.form.get('ca', 0))
                thal = float(request.form.get('thal', 0))
                
                user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
                prediction = predict_heart_disease(user_input)
                
                if prediction == 1:
                    diagnosis = "The person is having heart disease"
                else:
                    diagnosis = "The person does not have any heart disease"
                    
                from database.db import save_recommendation, save_report
                save_recommendation(user_id, diagnosis, "Heart Disease")
                
                inputs_dict = {
                    "Age": age, "Sex": sex, "Chest Pain Type": cp, "Resting Blood Pressure": trestbps,
                    "Cholesterol": chol, "Fasting Blood Sugar": fbs, "Rest ECG": restecg,
                    "Max Heart Rate": thalach, "Exercise Angina": exang
                }
                
                report_data = generate_ml_structured_report("Heart Disease", patient_info, inputs_dict, diagnosis)
                if report_data:
                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nAge: {age}, Cholestoral: {chol}, Max Heart Rate: {thalach}"
                    save_report(user_id, "Heart Disease Risk Assessment", report_content)

                # Save metrics for dashboard graphs
                save_assessment_metrics(user_id, 'heart', {
                    'Cholesterol': chol, 'Max Heart Rate': thalach,
                    'Resting BP': trestbps, 'Age': age
                }, prediction == 1)

                result = {"diagnosis": diagnosis, "is_positive": prediction == 1}
            except Exception as e:
                flash(f"Error processing heart disease assessment: {e}", "danger")
                
        elif assessment_type == "parkinsons":
            active_tab = "parkinsons"
            try:
                fo = float(request.form.get('fo', 0))
                fhi = float(request.form.get('fhi', 0))
                flo = float(request.form.get('flo', 0))
                Jitter_percent = float(request.form.get('jitter_percent', 0))
                Jitter_Abs = float(request.form.get('jitter_abs', 0))
                RAP = float(request.form.get('rap', 0))
                PPQ = float(request.form.get('ppq', 0))
                DDP = float(request.form.get('ddp', 0))
                Shimmer = float(request.form.get('shimmer', 0))
                Shimmer_dB = float(request.form.get('shimmer_db', 0))
                APQ3 = float(request.form.get('apq3', 0))
                APQ5 = float(request.form.get('apq5', 0))
                APQ = float(request.form.get('apq', 0))
                DDA = float(request.form.get('dda', 0))
                NHR = float(request.form.get('nhr', 0))
                HNR = float(request.form.get('hnr', 0))
                RPDE = float(request.form.get('rpde', 0))
                DFA = float(request.form.get('dfa', 0))
                spread1 = float(request.form.get('spread1', 0))
                spread2 = float(request.form.get('spread2', 0))
                D2 = float(request.form.get('d2', 0))
                PPE = float(request.form.get('ppe', 0))
                
                user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                              RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5,
                              APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]
                              
                prediction = predict_parkinsons(user_input)
                
                if prediction == 1:
                    diagnosis = "The person has Parkinson's disease"
                else:
                    diagnosis = "The person does not have Parkinson's disease"
                    
                from database.db import save_recommendation, save_report
                save_recommendation(user_id, diagnosis, "Parkinson's Disease")
                
                inputs_dict = {
                    "MDVP:Fo(Hz)": fo, "MDVP:Fhi(Hz)": fhi, "MDVP:Flo(Hz)": flo,
                    "MDVP:Jitter(%)": Jitter_percent, "MDVP:Jitter(Abs)": Jitter_Abs,
                    "MDVP:RAP": RAP, "MDVP:PPQ": PPQ, "Jitter:DDP": DDP
                }
                
                report_data = generate_ml_structured_report("Parkinson's Disease", patient_info, inputs_dict, diagnosis)
                if report_data:
                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nFo(Hz): {fo}, Fhi: {fhi}, Flo: {flo}"
                    save_report(user_id, "Parkinson's Risk Assessment", report_content)

                # Save metrics for dashboard graphs
                save_assessment_metrics(user_id, 'parkinsons', {
                    'MDVP:Fo(Hz)': fo, 'MDVP:Fhi(Hz)': fhi,
                    'MDVP:Flo(Hz)': flo, 'HNR': HNR, 'NHR': NHR
                }, prediction == 1)

                result = {"diagnosis": diagnosis, "is_positive": prediction == 1}
            except Exception as e:
                flash(f"Error processing Parkinson's assessment: {e}", "danger")

    return render_template("assessments.html", result=result, report_data=report_data, active_tab=active_tab)

@app.route("/reports")
@login_required
def reports():
    user_id = session['user_id']
    reports = get_reports(user_id)
    return render_template("reports.html", reports=reports)

@app.route("/reports/download/<int:report_id>")
@login_required
def download_report(report_id):
    user_id = session['user_id']
    from database.db import get_report_by_id
    report = get_report_by_id(report_id, user_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('reports'))
        
    from utils.pdf_generator import generate_simple_pdf
    from flask import send_file

    pdf_buffer = generate_simple_pdf(report['title'], report['content'])
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Healix_Report_{report_id}.pdf",
        mimetype="application/pdf"
    )

@app.route("/facilities", methods=["GET", "POST"])
@login_required
def facilities():
    location = request.args.get("location", "")
    disease = request.args.get("disease", "General")
    risk_level = request.args.get("risk_level", "Low")
    
    if request.method == "POST":
        location = request.form.get("location")
        disease = request.form.get("disease")
        risk_level = request.form.get("risk_level")
        
        from features.facility_recommender import get_healthcare_recommendations
        result = get_healthcare_recommendations(location, risk_level, disease)
        
        if "error" in result:
            return render_template("facilities.html", error=result["error"], location=location, disease=disease, risk_level=risk_level)
            
        return render_template("facilities.html", recommendations=result.get("data", []), location=location, disease=disease, risk_level=risk_level)
        
    return render_template("facilities.html", location=location, disease=disease, risk_level=risk_level)


if __name__ == "__main__":
    # Ensure database models are initialized by importing them here if necessary
    app.run(debug=True, port=8501)
