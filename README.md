# Hayat - Intelligent Disease Prediction & Health Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF4B4B)
![Gemini AI](https://img.shields.io/badge/Google%20GenAI-purple)
![License](https://img.shields.io/badge/License-MIT-green)

**Hayat** is a comprehensive, AI-powered health platform that seamlessly integrates Machine Learning for disease prediction and Generative AI for personalized health advice. Designed with a modern user interface, the application provides risk assessments, intelligent healthcare facility recommendations, and downloadable clinical reports.

## 🚀 Key Features

* **🛡️ Secure User Authentication:** Full user account management with secure signup, login, and encrypted password storage using bcrypt.
* **🤖 AI Health Chatbot:** An intelligent, conversational AI assistant powered by Google's GenAI model that answers health-related queries, offers lifestyle advice, and remembers your chat history.
* **🩺 Disease Prediction Models:** Use carefully trained Machine Learning models to assess risks:
  * **Diabetes:** Assesses probability based on Glucose, BMI, Insulin, Age, and more.
  * **Heart Disease:** Predicts cardiovascular risks using Resting BP, Cholesterol, Max Heart Rate, etc.
  * **Parkinson's Disease:** Detects early signs using multidimensional voice measurement data.
* **🏥 Intelligent Location-Based Recommendations:** After a risk assessment, the application suggests the top nearby care facilities (Hospitals for high risk, Clinics for moderate risk, General Physicians for low risk) using the Geoapify API.
* **📄 Clinical PDF Reports:** Easily generate, view, and download professional-grade PDF clinical reports based on your AI and ML assessment results.
* **📊 Comprehensive User Dashboard:** Manage personal health profiles, access saved reports, review past disease recommendations, and keep track of all health interactions in one unified dashboard.

## 🛠️ Technology Stack

* **Frontend:** Streamlit, Streamlit Option Menu, Custom CSS (Dark/Light mode optimized)
* **AI Integration:** Google GenAI (`google-genai`)
* **Machine Learning:** Scikit-learn, Numpy, Pandas
* **Database:** SQLite (with structured models for users, vitals, chat history, and reports)
* **PDF Generation:** ReportLab
* **Location Services:** Geoapify API
* **Security:** Bcrypt, Python-dotenv

## 📂 Project Structure

```
├── app.py                      # Main Streamlit application and router
├── auth/                       # User authentication and session management
├── database/                   # SQLite database initialization and models
├── features/                   # Core business logic (chatbot, predictions, facility recommender, report generator)
├── pages/                      # Streamlit UI pages (Dashboard, Chat, Profile, Recommendations, Reports, History)
├── utils/                      # Helper scripts (PDF generator, CSS loader)
├── assets/                     # Images, CSS files, and other static assets
├── saved_models/               # Pre-trained ML models (.sav)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/huzaiif/Health-GPT.git
   cd Health-GPT
   ```

2. **Install Dependencies**
   Ensure you have Python installed (3.8+ recommended). It's best practice to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   * Create a `.env` file in the root directory.
   * Add your API keys required for the AI and location services:
     ```env
     GOOGLE_API_KEY=your_gemini_api_key_here
     GEOAPIFY_API_KEY=your_geoapify_api_key_here
     ```

4. **Initialize Database and Run Application**
   ```bash
   # In terminal, run the streamlit app
   streamlit run app.py
   ```
   *The database `health_gpt.db` will be auto-generated upon the application's first run.*

## 🧠 How It Works

1. **Registration & Login:** Securely log in to access your personalized health dashboard.
2. **Setup Profile:** Enter your baseline medical history and body metrics.
3. **Use the Assistant:** Chat directly with the AI for instant health insights.
4. **Take Risk Assessments:** Enter lab values into the ML prediction tabs for Diabetes, Heart Disease, or Parkinson's. 
5. **Get Advice & Recommendations:** Receive an AI-generated clinical summary, download it as a PDF, and explore suggested healthcare providers natively near your location.

## ⚠️ Medical Disclaimer

**Hayat is an informational tool and NOT a substitute for professional medical advice, diagnosis, or treatment.**
* The predictions rely on machine learning models and may not necessarily represent actual medical diagnosis.
* Always consult with a qualified healthcare provider for any medical concerns or before making any health-related decisions.
* In case of a medical emergency, contact your local emergency services immediately.

## 👨‍💻 Author

**Huzaif**
