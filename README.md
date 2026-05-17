# Healix - Intelligent Disease Prediction & Premium AI Health Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey?style=for-the-badge&logo=flask&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Auth-emerald?style=for-the-badge&logo=supabase&logoColor=white)
![Groq Llama 3](https://img.shields.io/badge/Groq%20AI-Llama%203.3-orange?style=for-the-badge&logo=meta&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Healix** is a premium, AI-powered health platform that seamlessly integrates advanced Machine Learning classification models for disease risk assessment with a Generative AI clinical assistant. Designed with a dark SaaS-grade aesthetic, Healix provides dynamic predictive analytics, intelligent healthcare facility recommendations, session-based AI consults, and downloadable clinical PDF reports.

---

## 🚀 Key Features

* **🛡️ Cloud Auth & Session Management:** Integrated secure user management (Sign Up, Login, Forgot & Reset Password) powered securely by **Supabase Auth**.
* **🤖 Session-Based AI Assistant:** Conversational medical consults powered by the high-speed **Groq API (Llama 3.3 70B)**. Includes a session history drawer to create, manage, or delete chat threads.
* **🩺 Disease Risk Classifiers:** Predictive Machine Learning models trained to classify patient risks:
  * **Diabetes:** Risk assessment based on Glucose, BMI, Insulin, Age, etc.
  * **Heart Disease:** Cardiovascular risk evaluation utilizing resting BP, cholesterol, max heart rate, and chest pain indicators.
  * **Parkinson's Disease:** Early symptom detection using multidimensional acoustic voice measurement data.
* **📊 Dynamic Health Trend Analytics:** Real-time user dashboards featuring interactive **Chart.js** telemetry representing risk indicators and historical health trends across successive assessments.
* **🏥 Geo-Location Care Recommender:** Location-based healthcare recommendations natively suggesting the most relevant care provider based on assessment severity (Hospitals for High risk, Clinics for Moderate, General Practitioners for Low) utilizing the **Geoapify API**.
* **📄 Downloadable PDF Clinical Reports:** Generate instant, professional-grade clinical summaries compiled on demand with **ReportLab** ready for local downloading.

---

## 🛠️ Technology Stack

* **Backend:** Flask (Python)
* **Frontend:** Responsive HTML5, Vanilla CSS3 (Premium dark-theme SaaS design), JavaScript (ES6+), and **Chart.js**
* **Cloud Database & Authentication:** Supabase (PostgreSQL Client)
* **LLM Engine:** Groq SDK (`llama-3.3-70b-versatile`)
* **Machine Learning:** Scikit-learn, Numpy
* **PDF Report Generation:** ReportLab
* **APIs:** Geoapify REST API (Facility Recommendations)

---

## 📂 Project Structure

```
├── app.py                      # Flask backend controller and routing
├── database/
│   └── db.py                   # Supabase integration layers and DB operations
├── features/
│   ├── chatbot.py              # Groq assistant backend integration
│   ├── recommendation.py       # Scikit-learn predictive ML models logic
│   ├── facility_recommender.py # Geoapify location recommended care engine
│   └── report_generator.py     # AI clinical text summaries generation
├── templates/                  # Jinja2 Flask web page views
│   ├── base.html               # Global UI wrapper & layout
│   ├── dashboard.html          # Health metrics graphs and analytics dashboard
│   ├── chat.html               # Unified AI Assistant chat interface
│   ├── chat_widget.html        # Floating quick-chat overlay
│   ├── assessments.html        # Multi-tab disease risk diagnostic inputs
│   └── ...                     # Auth wrappers (login, register, reset password)
├── static/
│   ├── style.css               # Global premium dark-theme stylesheet
│   └── script.js               # Global DOM animations and theme engine
├── saved_models/               # Serialized ML classification models (.sav)
├── utils/
│   ├── helpers.py              # Load-environment configuration variables helper
│   └── pdf_generator.py        # PDF compilation layout engine
├── requirements.txt            # Python dependencies manifest
└── README.md                   # Project documentation
```

---

## ⚙️ Installation & Local Setup

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/huzaiif/Healix.git
cd Healix
```

### 2. Configure Virtual Environment
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root directory:
```env
# Flask
FLASK_SECRET_KEY=your_flask_session_key

# Supabase Configurations
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# API Integrations
GROQ_API_KEY=gsk_your_groq_api_key
GEOAPIFY_API_KEY=your_geoapify_key
```

### 5. Launch the Server
```bash
python app.py
```
*Your application will start on **`http://127.0.0.1:8501`**.*

---

## ⚠️ Medical Disclaimer

**Healix is strictly an informational and educational risk-assessment utility. It is NOT a substitute for professional medical advice, clinical diagnosis, or medical treatment.**
* Predictive diagnostics are powered by automated ML classification models and do not serve as professional medical validations.
* Always consult with a licensed physician or clinical expert before initiating any dietary, pharmaceutical, or clinical health adjustments.
* In the event of a medical emergency, contact your local emergency response service immediately.

---

## 👨‍💻 Author

Developed with ❤️ by **Huzaif**
