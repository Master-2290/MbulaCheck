from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
import os
import io
from datetime import date, timedelta, datetime

from models.utils import add_temporal_features, add_lags

# --------------------------
# Initialisation de l'app
# --------------------------
app = FastAPI(
    title="MbulaCheck API 🌦️",
    description="API pour prédire la météo et la pluie à Kinshasa à partir de la date ou d'une période.",
    version="2.0.0"
)

# --------------------------
# Chargement des modèles et données historiques
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "nasa_weather_2018_2025.csv")

try:
    REGRESSOR_PATH = os.path.join(MODEL_DIR, "MbulaCheck_regressor.pkl")
    CLASSIFIER_PATH = os.path.join(MODEL_DIR, "MbulaCheck_classifier.pkl")
    regressor = joblib.load(REGRESSOR_PATH)
    classifier = joblib.load(CLASSIFIER_PATH)
    print("✅ Modèles chargés avec succès.")
except Exception as e:
    print("❌ Erreur lors du chargement des modèles :", e)
    regressor, classifier = None, None

try:
    df_hist = pd.read_csv(DATA_PATH, parse_dates=["date"])
    print("✅ Historique météo chargé.")
except Exception as e:
    print("❌ Erreur chargement de l'historique météo:", e)
    df_hist = None

# --------------------------
# Helper : Préparer les features pour une date/période
# --------------------------


def build_features_for_date(date_val, lags=[1, 3]):
    date_val = pd.to_datetime(date_val)
    needed_dates = [date_val - pd.Timedelta(days=lag) for lag in lags]
    for lag, d in zip(lags, needed_dates):
        if d not in df_hist['date'].values:
            return None  # données manquantes
    row = df_hist[df_hist['date'] == date_val].copy()
    if row.empty:
        return None
    row = add_temporal_features(row, date_col='date')
    df_with = pd.concat([df_hist, row], ignore_index=True)
    df_with = add_lags(df_with, ["Temperature_C", "Humidity_percent",
                       "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"], lags=lags)
    last_row = df_with[df_with['date'] == date_val]
    return last_row


def build_features_for_period(start_date, end_date, lags=[1, 3]):
    period = pd.date_range(start=start_date, end=end_date)
    features = []
    for d in period:
        row = build_features_for_date(d, lags=lags)
        if row is not None and not row.empty:
            features.append(row)
    if features:
        return pd.concat(features, ignore_index=True)
    else:
        return pd.DataFrame()

# --------------------------
# Endpoint racine
# --------------------------


@app.get("/")
def home():
    return {"message": "Bienvenue sur l’API MbulaCheck v2 🌍. Rendez-vous sur /docs pour tester."}

# --------------------------
# Endpoint de prédiction sur une période
# --------------------------


class PredictionRequest(BaseModel):
    start_date: date = Field(...,
                             description="Date de début au format YYYY-MM-DD")
    end_date: date = Field(..., description="Date de fin au format YYYY-MM-DD")


@app.post("/predict/period")
def predict_period(req: PredictionRequest):
    if regressor is None or classifier is None or df_hist is None:
        raise HTTPException(
            status_code=500, detail="Modèles ou données historiques non disponibles.")

    # Validation des dates
    if req.end_date < req.start_date:
        raise HTTPException(
            status_code=400, detail="La date de fin doit être après la date de début.")
    # Préparation des features
    features_df = build_features_for_period(req.start_date, req.end_date)
    if features_df.empty:
        raise HTTPException(
            status_code=400, detail="Impossible de générer les features pour cette période (données historiques manquantes).")

    # Sélection des colonnes d'entrée
    input_cols = [c for c in features_df.columns if c not in [
        "date", "Temperature_C", "Humidity_percent", "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"]]
    X = features_df[input_cols]

    # Prédictions
    y_reg = regressor.predict(X)
    y_clf_proba = classifier.predict_proba(X)[:, 1]

    # Résultats
    results = []
    for i, row in features_df.iterrows():
        results.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "Temperature_C": round(float(y_reg[i, 0]), 2),
            "Humidity_percent": round(float(y_reg[i, 1]), 2),
            "Pressure_kPa": round(float(y_reg[i, 2]), 2),
            "Wind_m_s": round(float(y_reg[i, 3]), 2),
            "Rain_Probability": round(float(y_clf_proba[i]), 3)
        })
    return {"results": results}

# --------------------------
# Endpoint téléchargement CSV ou JSON
# --------------------------


@app.get("/download")
def download_results(
        start_date: date = Query(..., description="Date de début YYYY-MM-DD"),
        end_date: date = Query(..., description="Date de fin YYYY-MM-DD"),
        format: str = Query("csv", description="Format: csv ou json")):
    if regressor is None or classifier is None or df_hist is None:
        raise HTTPException(
            status_code=500, detail="Modèles ou données historiques non disponibles.")
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="La date de fin doit être après la date de début.")
    features_df = build_features_for_period(start_date, end_date)
    if features_df.empty:
        raise HTTPException(
            status_code=400, detail="Impossible de générer les features pour cette période (données historiques manquantes).")
    input_cols = [c for c in features_df.columns if c not in [
        "date", "Temperature_C", "Humidity_percent", "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"]]
    X = features_df[input_cols]
    y_reg = regressor.predict(X)
    y_clf_proba = classifier.predict_proba(X)[:, 1]
    df_out = pd.DataFrame({
        "date": features_df["date"].dt.strftime("%Y-%m-%d"),
        "Temperature_C": y_reg[:, 0],
        "Humidity_percent": y_reg[:, 1],
        "Pressure_kPa": y_reg[:, 2],
        "Wind_m_s": y_reg[:, 3],
        "Rain_Probability": y_clf_proba
    })
    if format == "csv":
        stream = io.StringIO()
        df_out.to_csv(stream, index=False)
        stream.seek(0)
        return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=mbulacheck_results.csv"})
    elif format == "json":
        return JSONResponse(df_out.to_dict(orient="records"))
    else:
        raise HTTPException(
            status_code=400, detail="Format non supporté (csv ou json attendu)")

# --------------------------
# Endpoint statistiques sur la période
# --------------------------


@app.get("/period/stats")
def stats_period(
        start_date: date = Query(..., description="Date de début YYYY-MM-DD"),
        end_date: date = Query(..., description="Date de fin YYYY-MM-DD")):
    if regressor is None or classifier is None or df_hist is None:
        raise HTTPException(
            status_code=500, detail="Modèles ou données historiques non disponibles.")
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="La date de fin doit être après la date de début.")
    features_df = build_features_for_period(start_date, end_date)
    if features_df.empty:
        raise HTTPException(
            status_code=400, detail="Impossible de générer les features pour cette période (données historiques manquantes).")
    input_cols = [c for c in features_df.columns if c not in [
        "date", "Temperature_C", "Humidity_percent", "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"]]
    X = features_df[input_cols]
    y_reg = regressor.predict(X)
    y_clf_proba = classifier.predict_proba(X)[:, 1]
    df_out = pd.DataFrame({
        "date": features_df["date"].dt.strftime("%Y-%m-%d"),
        "Temperature_C": y_reg[:, 0],
        "Humidity_percent": y_reg[:, 1],
        "Pressure_kPa": y_reg[:, 2],
        "Wind_m_s": y_reg[:, 3],
        "Rain_Probability": y_clf_proba
    })
    # Statistiques simples
    stats = {
        "Temperature_C_mean": round(df_out["Temperature_C"].mean(), 2),
        "Temperature_C_max": round(df_out["Temperature_C"].max(), 2),
        "Temperature_C_min": round(df_out["Temperature_C"].min(), 2),
        "Humidity_percent_mean": round(df_out["Humidity_percent"].mean(), 2),
        "Pressure_kPa_mean": round(df_out["Pressure_kPa"].mean(), 2),
        "Wind_m_s_mean": round(df_out["Wind_m_s"].mean(), 2),
        "Nb_days_rain_proba_gt_0.6": int((df_out["Rain_Probability"] > 0.6).sum())
    }
    return stats
