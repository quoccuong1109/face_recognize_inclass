import joblib

def load_model():
    model_path = 'models/face_recognition_model.pkl'
    model = joblib.load(model_path)
    return model