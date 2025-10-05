from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
import traceback

# --------------------------
# Initialisation de l'app
# --------------------------
app = FastAPI(
    title="MbulaCheck API 🌦️",
    description="API pour prédire la météo et la pluie à Kinshasa à partir des données météo.",
    version="1.0.1"
)

# --------------------------
# Chargement des modèles
# --------------------------
try:
    # Détermination du chemin absolu
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

    REGRESSOR_PATH = os.path.join(MODEL_DIR, "MbulaCheck_regressor.pkl")
    CLASSIFIER_PATH = os.path.join(MODEL_DIR, "MbulaCheck_classifier.pkl")

    regressor = joblib.load(REGRESSOR_PATH)
    classifier = joblib.load(CLASSIFIER_PATH)

    print("✅ Modèles chargés avec succès.")
except Exception as e:
    print("❌ Erreur lors du chargement des modèles :", e)
    traceback.print_exc()
    regressor, classifier = None, None


# --------------------------
# Schéma d'entrée
# --------------------------
class WeatherFeatures(BaseModel):
    dayofyear: int
    month: int
    year: int
    dayofweek: int
    T2M_lag1: float
    T2M_lag3: float
    RH2M_lag1: float
    RH2M_lag3: float
    PS_lag1: float
    PS_lag3: float
    WS2M_lag1: float
    WS2M_lag3: float
    PRECTOTCORR_lag1: float
    PRECTOTCORR_lag3: float


# --------------------------
# Endpoint racine
# --------------------------
@app.get("/")
def home():
    return {"message": "Bienvenue sur l’API MbulaCheck 🌍. Rendez-vous sur /docs pour tester."}


# --------------------------
# Endpoint Régression
# --------------------------
@app.post("/predict/regression")
def predict_regression(features: WeatherFeatures):
    if regressor is None:
        raise HTTPException(
            status_code=500, detail="Modèle de régression non chargé.")

    try:
        data = np.array([list(features.dict().values())])
        prediction = regressor.predict(data)[0]

        return {
            "Temperature_C": round(float(prediction[0]), 2),
            "Humidity_percent": round(float(prediction[1]), 2),
            "Pressure_kPa": round(float(prediction[2]), 2),
            "Wind_m_s": round(float(prediction[3]), 2)
        }

    except Exception as e:
        print("❌ Erreur pendant la prédiction de régression :", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Endpoint Classification (Pluie)
# --------------------------
@app.post("/predict/classification")
def predict_classification(features: WeatherFeatures):
    if classifier is None:
        raise HTTPException(
            status_code=500, detail="Modèle de classification non chargé.")

    try:
        data = np.array([list(features.dict().values())])
        prob = classifier.predict_proba(data)[0][1]
        prediction = int(prob > 0.5)

        return {
            "Rain_Prediction": "🌧️ Oui" if prediction == 1 else "☀️ Non",
            "Probability": round(float(prob), 3)
        }

    except Exception as e:
        print("❌ Erreur pendant la prédiction de classification :", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
