from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("fraud_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.post("/predict")
def predict(data: dict):

    features = np.array([[ 
        data["amount"],
        data["hour"],
        data["locationRisk"],
        data["velocityScore"]
    ]])

    features_scaled = scaler.transform(features)

    probability = model.predict_proba(features_scaled)[0][1]

    return {
        "fraudProbability": float(probability)
    }