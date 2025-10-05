import pandas as pd
import numpy as np
import joblib

# --------------------------
# 1) Features temporelles
# --------------------------
def add_temporal_features(df, date_col="date"):
    """
    Ajoute des features temporelles sinus/cos pour la saisonnalité.
    """
    df = df.copy()
    df["dayofyear"] = df[date_col].dt.dayofyear
    df["sin_doy"] = np.sin(2 * np.pi * df["dayofyear"] / 365.25)
    df["cos_doy"] = np.cos(2 * np.pi * df["dayofyear"] / 365.25)
    return df

# --------------------------
# 2) Lags pour les séries temporelles
# --------------------------
def add_lags(df, cols, lags=[1,3,7]):
    """
    Ajoute des colonnes décalées (lags) pour chaque variable.
    df : dataframe
    cols : liste de colonnes à transformer
    lags : liste d'entiers (nombre de jours de lag)
    """
    df = df.copy()
    for col in cols:
        for lag in lags:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)
    df = df.dropna()
    return df

# --------------------------
# 3) Sauvegarde / chargement modèle
# --------------------------
def save_model(model, filepath):
    """Sauvegarde un modèle ML avec joblib"""
    joblib.dump(model, filepath)

def load_model(filepath):
    """Charge un modèle ML avec joblib"""
    return joblib.load(filepath)

# --------------------------
# 4) Préparation des nouvelles données pour l'inférence
# --------------------------
def prepare_input(new_data):
    """
    Prépare un dataframe de nouvelles données pour l'inférence.
    new_data : dataframe avec colonnes brutes NASA
    """
    df = add_temporal_features(new_data)
    lag_cols = ["Temperature_C", "Humidity_percent", "Pressure_kPa", "Wind_m_s", "Precipitation_mm"]
    df = add_lags(df, lag_cols, lags=[1,3])
    return df
