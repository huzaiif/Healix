import os
import pickle
import warnings
import streamlit as st
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", message=".*does not have valid feature names.*")

@st.cache_resource
def load_prediction_models():
    working_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    diabetes_model_path = os.path.join(working_dir, 'saved_models', 'diabetes_model.sav')
    heart_disease_model_path = os.path.join(working_dir, 'saved_models', 'heart_disease_model.sav')
    parkinsons_model_path = os.path.join(working_dir, 'saved_models', 'parkinsons_model.sav')
    
    diabetes_model = pickle.load(open(diabetes_model_path, 'rb'))
    heart_disease_model = pickle.load(open(heart_disease_model_path, 'rb'))
    parkinsons_model = pickle.load(open(parkinsons_model_path, 'rb'))
    
    return diabetes_model, heart_disease_model, parkinsons_model

def predict_diabetes(user_input):
    models = load_prediction_models()
    diabetes_model = models[0]
    prediction = diabetes_model.predict([user_input])
    return prediction[0]

def predict_heart_disease(user_input):
    models = load_prediction_models()
    heart_disease_model = models[1]
    prediction = heart_disease_model.predict([user_input])
    return prediction[0]

def predict_parkinsons(user_input):
    models = load_prediction_models()
    parkinsons_model = models[2]
    prediction = parkinsons_model.predict([user_input])
    return prediction[0]
