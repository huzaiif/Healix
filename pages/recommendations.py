import streamlit as st
from features.recommendation import predict_diabetes, predict_heart_disease, predict_parkinsons
from features.chatbot import generate_health_tips
from database.db import save_recommendation, save_report

def render_facility_recommendations(disease_name: str, risk_level: str, tab_key: str):
    st.markdown("<hr style='margin: 2rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    st.subheader("🏥 Find Nearby Healthcare Facilities")
    st.markdown(f"Based on your **{risk_level}** risk assessment, we can recommend appropriate care.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        location = st.text_input("Enter your city or zip code:", key=f"loc_input_{tab_key}", placeholder="e.g., New York, NY")
    with col2:
        st.write("")
        st.write("")
        search_pressed = st.button("Search Options", key=f"btn_search_{tab_key}", use_container_width=True)
        
    if search_pressed and location:
        with st.spinner(f"Finding best options near {location}..."):
            from features.facility_recommender import get_healthcare_recommendations
            result = get_healthcare_recommendations(location, risk_level, disease_name)
            
            if "error" in result:
                st.error(result["error"])
            elif not result.get("data"):
                st.warning("No facilities found nearby.")
            else:
                st.success(f"Found top matches for **{result['data'][0]['care_type']}** near {location}")
                
                cols = st.columns(3)
                for i, rec in enumerate(result["data"]):
                    with cols[i]:
                        st.markdown(f'''
                        <div class="facility-card">
                            <div class="facility-img-container">
                                <img src="{rec['image_url']}" class="facility-img" alt="{rec['care_type']}">
                            </div>
                            <div class="facility-content">
                                <h4 class="facility-title">{rec['name']}</h4>
                                <div class="facility-meta">
                                    <span class="facility-badge">{rec['care_type']}</span>
                                    <span class="facility-distance">📍 {rec['distance_miles']} mi</span>
                                </div>
                                <p class="facility-address">{rec['address']}</p>
                                <p class="facility-reason"><strong>Why:</strong> {rec['reason']}</p>
                                <a href="{rec['maps_url']}" target="_blank" class="facility-btn">🗺️ Open in Maps</a>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

def show_recommendations():
    st.title("Disease Risk Assessment 🩺")
    st.markdown("Use our ML models to assess your risk for specific conditions.")
    
    user_id = st.session_state['user_id']
    
    tab1, tab2, tab3 = st.tabs(["Diabetes", "Heart Disease", "Parkinson's"])
    
    with tab1:
        st.subheader("Diabetes Prediction")
        col1, col2, col3 = st.columns(3)
        with col1:
            Pregnancies = st.number_input('Number of Pregnancies', min_value=0, step=1)
            SkinThickness = st.number_input('Skin Thickness value', min_value=0.0)
            DiabetesPedigreeFunction = st.number_input('Diabetes Pedigree Function value', min_value=0.0)
        with col2:
            Glucose = st.number_input('Glucose Level', min_value=0.0)
            Insulin = st.number_input('Insulin Level', min_value=0.0)
            Age = st.number_input('Age of the Person', min_value=1, step=1)
        with col3:
            BloodPressure = st.number_input('Blood Pressure value', min_value=0.0)
            BMI = st.number_input('BMI value', min_value=0.0)
            
        if st.button('Diabetes Test Result', use_container_width=True):
            user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                          BMI, DiabetesPedigreeFunction, Age]
            
            prediction = predict_diabetes(user_input)
            
            if prediction == 1:
                diagnosis = 'The person is diabetic'
                st.error(diagnosis)
            else:
                diagnosis = 'The person is not diabetic'
                st.success(diagnosis)
                
            save_recommendation(user_id, diagnosis, "Diabetes")
            
            st.subheader("Clinical AI Report & Advice")
            with st.spinner("Generating structured report..."):
                patient_info = {"patient_id": f"PT-{user_id:04d}", "age": Age, "gender": "Unknown"}
                inputs_dict = {
                    "Pregnancies": Pregnancies, "Glucose": Glucose, "Blood Pressure": BloodPressure,
                    "Skin Thickness": SkinThickness, "Insulin": Insulin, "BMI": BMI,
                    "Diabetes Pedigree Function": DiabetesPedigreeFunction, "Age": Age
                }
                
                from features.report_generator import generate_ml_structured_report
                report_data = generate_ml_structured_report("Diabetes", patient_info, inputs_dict, diagnosis)
                
                if report_data:
                    import uuid
                    from datetime import datetime
                    report_data["report_id"] = str(uuid.uuid4())
                    st.session_state['diabetes_report'] = report_data
                    st.session_state['diabetes_diagnosis'] = diagnosis

                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nPregnancies: {Pregnancies}, Glucose: {Glucose}, BP: {BloodPressure}, BMI: {BMI}"
                    save_report(user_id, "Diabetes Risk Assessment", report_content)

        if 'diabetes_report' in st.session_state:
            report_data = st.session_state['diabetes_report']
            
            analysis = report_data.get('ai_analysis', {})
            st.info(analysis.get('summary', ''))
            
            risk_level = analysis.get('risk_level', 'Unknown')
            risk_color = "red" if str(risk_level).lower() == "high" else ("orange" if str(risk_level).lower() == "moderate" else "green")
            st.markdown(f"**Risk Level:** <span style='color:{risk_color}; font-weight:bold;'>{str(risk_level).upper()}</span>", unsafe_allow_html=True)
            
            recs = report_data.get('recommendations', {})
            if recs.get('immediate_actions'):
                 st.warning("**Immediate Actions:**\n" + "\n".join([f"- {x}" for x in recs.get('immediate_actions', [])]))
                 
            from utils.pdf_generator import generate_clinical_pdf
            pdf_buffer = generate_clinical_pdf(report_data)
            from datetime import datetime
            st.download_button(
                label="⬇️ Download Official PDF Report",
                data=pdf_buffer,
                file_name=f"diabetes_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            render_facility_recommendations("Diabetes", risk_level, "diabetes")
                
    with tab2:
        st.subheader("Heart Disease Prediction")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input('Age', min_value=1, step=1, key="hd_age")
            trestbps = st.number_input('Resting Blood Pressure', min_value=0.0)
            restecg = st.number_input('Resting Electrocardiographic results', min_value=0.0)
            oldpeak = st.number_input('ST depression induced by exercise', min_value=0.0)
            thal = st.number_input('thal: 0 = normal; 1 = fixed defect; 2 = reversable defect', min_value=0, max_value=2, step=1)
        with col2:
            sex = st.number_input('Sex (1=Male, 0=Female)', min_value=0, max_value=1, step=1)
            chol = st.number_input('Serum Cholestoral in mg/dl', min_value=0.0)
            thalach = st.number_input('Maximum Heart Rate achieved', min_value=0.0)
            slope = st.number_input('Slope of the peak exercise ST segment', min_value=0.0)
        with col3:
            cp = st.number_input('Chest Pain types', min_value=0, step=1)
            fbs = st.number_input('Fasting Blood Sugar > 120 mg/dl (1=true, 0=false)', min_value=0, max_value=1, step=1)
            exang = st.number_input('Exercise Induced Angina (1=yes, 0=no)', min_value=0, max_value=1, step=1)
            ca = st.number_input('Major vessels colored by flourosopy', min_value=0, step=1)

        if st.button('Heart Disease Test Result', use_container_width=True):
            user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
            
            prediction = predict_heart_disease(user_input)
            
            if prediction == 1:
                diagnosis = 'The person is having heart disease'
                st.error(diagnosis)
            else:
                diagnosis = 'The person does not have any heart disease'
                st.success(diagnosis)
                
            save_recommendation(user_id, diagnosis, "Heart Disease")

            st.subheader("Clinical AI Report & Advice")
            with st.spinner("Generating structured report..."):
                patient_info = {"patient_id": f"PT-{user_id:04d}", "age": age, "gender": "Male" if sex==1 else "Female"}
                inputs_dict = {
                    "Age": age, "Sex": sex, "Chest Pain Type": cp, "Resting Blood Pressure": trestbps,
                    "Cholesterol": chol, "Fasting Blood Sugar": fbs, "Rest ECG": restecg,
                    "Max Heart Rate": thalach, "Exercise Angina": exang
                }
                
                from features.report_generator import generate_ml_structured_report
                report_data = generate_ml_structured_report("Heart Disease", patient_info, inputs_dict, diagnosis)
                
                if report_data:
                    import uuid
                    from datetime import datetime
                    report_data["report_id"] = str(uuid.uuid4())
                    st.session_state['heart_report'] = report_data
                    st.session_state['heart_diagnosis'] = diagnosis

                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nAge: {age}, Cholestoral: {chol}, Max Heart Rate: {thalach}"
                    save_report(user_id, "Heart Disease Risk Assessment", report_content)

        if 'heart_report' in st.session_state:
            report_data = st.session_state['heart_report']
            
            analysis = report_data.get('ai_analysis', {})
            st.info(analysis.get('summary', ''))
            
            risk_level = analysis.get('risk_level', 'Unknown')
            risk_color = "red" if str(risk_level).lower() == "high" else ("orange" if str(risk_level).lower() == "moderate" else "green")
            st.markdown(f"**Risk Level:** <span style='color:{risk_color}; font-weight:bold;'>{str(risk_level).upper()}</span>", unsafe_allow_html=True)
            
            recs = report_data.get('recommendations', {})
            if recs.get('immediate_actions'):
                 st.warning("**Immediate Actions:**\n" + "\n".join([f"- {x}" for x in recs.get('immediate_actions', [])]))
                 
            from utils.pdf_generator import generate_clinical_pdf
            pdf_buffer = generate_clinical_pdf(report_data)
            from datetime import datetime
            st.download_button(
                label="⬇️ Download Official PDF Report",
                data=pdf_buffer,
                file_name=f"heart_disease_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            render_facility_recommendations("Heart Disease", risk_level, "heart")

    with tab3:
        st.subheader("Parkinson's Disease Prediction")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            fo = st.number_input('MDVP:Fo(Hz)', min_value=0.0)
            RAP = st.number_input('MDVP:RAP', min_value=0.0)
            APQ3 = st.number_input('Shimmer:APQ3', min_value=0.0)
            HNR = st.number_input('HNR', min_value=0.0)
            D2 = st.number_input('D2', min_value=0.0)
        with col2:
            fhi = st.number_input('MDVP:Fhi(Hz)', min_value=0.0)
            PPQ = st.number_input('MDVP:PPQ', min_value=0.0)
            APQ5 = st.number_input('Shimmer:APQ5', min_value=0.0)
            RPDE = st.number_input('RPDE', min_value=0.0)
            PPE = st.number_input('PPE', min_value=0.0)
        with col3:
            flo = st.number_input('MDVP:Flo(Hz)', min_value=0.0)
            DDP = st.number_input('Jitter:DDP', min_value=0.0)
            APQ = st.number_input('MDVP:APQ', min_value=0.0)
            DFA = st.number_input('DFA', min_value=0.0)
        with col4:
            Jitter_percent = st.number_input('MDVP:Jitter(%)', min_value=0.0)
            Shimmer = st.number_input('MDVP:Shimmer', min_value=0.0)
            DDA = st.number_input('Shimmer:DDA', min_value=0.0)
            spread1 = st.number_input('spread1', value=0.0)
        with col5:
            Jitter_Abs = st.number_input('MDVP:Jitter(Abs)', min_value=0.0)
            Shimmer_dB = st.number_input('MDVP:Shimmer(dB)', min_value=0.0)
            NHR = st.number_input('NHR', min_value=0.0)
            spread2 = st.number_input('spread2', value=0.0)

        if st.button("Parkinson's Test Result", use_container_width=True):
            user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                          RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5,
                          APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]
            
            prediction = predict_parkinsons(user_input)
            
            if prediction == 1:
                diagnosis = "The person has Parkinson's disease"
                st.error(diagnosis)
            else:
                diagnosis = "The person does not have Parkinson's disease"
                st.success(diagnosis)
                
            save_recommendation(user_id, diagnosis, "Parkinson's Disease")

            st.subheader("Clinical AI Report & Advice")
            with st.spinner("Generating structured report..."):
                patient_info = {"patient_id": f"PT-{user_id:04d}", "age": "Unknown", "gender": "Unknown"}
                inputs_dict = {
                    "MDVP:Fo(Hz)": fo, "MDVP:Fhi(Hz)": fhi, "MDVP:Flo(Hz)": flo,
                    "MDVP:Jitter(%)": Jitter_percent, "MDVP:Jitter(Abs)": Jitter_Abs,
                    "MDVP:RAP": RAP, "MDVP:PPQ": PPQ, "Jitter:DDP": DDP
                }
                
                from features.report_generator import generate_ml_structured_report
                report_data = generate_ml_structured_report("Parkinson's Disease", patient_info, inputs_dict, diagnosis)
                
                if report_data:
                    import uuid
                    from datetime import datetime
                    report_data["report_id"] = str(uuid.uuid4())
                    st.session_state['parkinsons_report'] = report_data
                    st.session_state['parkinsons_diagnosis'] = diagnosis
                    
                    report_content = f"**Diagnosis:** {diagnosis}\n\n**Risk Level:** {report_data.get('ai_analysis', {}).get('risk_level', 'Unknown')}\n\n**Summary:**\n{report_data.get('ai_analysis', {}).get('summary', '')}\n\n**Inputs:**\nFo(Hz): {fo}, Fhi: {fhi}, Flo: {flo}"
                    save_report(user_id, "Parkinson's Risk Assessment", report_content)

        if 'parkinsons_report' in st.session_state:
            report_data = st.session_state['parkinsons_report']
            
            analysis = report_data.get('ai_analysis', {})
            st.info(analysis.get('summary', ''))
            
            risk_level = analysis.get('risk_level', 'Unknown')
            risk_color = "red" if str(risk_level).lower() == "high" else ("orange" if str(risk_level).lower() == "moderate" else "green")
            st.markdown(f"**Risk Level:** <span style='color:{risk_color}; font-weight:bold;'>{str(risk_level).upper()}</span>", unsafe_allow_html=True)
            
            recs = report_data.get('recommendations', {})
            if recs.get('immediate_actions'):
                 st.warning("**Immediate Actions:**\n" + "\n".join([f"- {x}" for x in recs.get('immediate_actions', [])]))
                 
            from utils.pdf_generator import generate_clinical_pdf
            pdf_buffer = generate_clinical_pdf(report_data)
            from datetime import datetime
            st.download_button(
                label="⬇️ Download Official PDF Report",
                data=pdf_buffer,
                file_name=f"parkinsons_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            render_facility_recommendations("Parkinson's Disease", risk_level, "parkinsons")

if __name__ == "__main__":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        show_recommendations()
    else:
        st.warning("Please log in to view this page.")
