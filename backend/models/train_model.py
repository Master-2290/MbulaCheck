import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, roc_auc_score
import joblib
import os
import sys

# Import utils perso
try:
    from utils import add_temporal_features, add_lags, save_model
except ImportError as e:
    print("❌ Erreur : Impossible d'importer utils.py. Vérifie qu'il est bien dans backend/")
    sys.exit(1)

# --------------------------
# 1) Charger les données
# --------------------------

# Détermination automatique du chemin du fichier CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'nasa_weather_2018_2025.csv')

try:
    # Lecture directe du CSV (pas besoin de double lecture)
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    print(
        f"✅ Données chargées avec succès : {df.shape[0]} lignes, {df.shape[1]} colonnes")
except Exception as e:
    print(f"❌ Erreur lors du chargement des données : {e}")
    sys.exit(1)

# --------------------------
# 2) Features temporelles + Lags
# --------------------------
try:
    df = add_temporal_features(df, date_col="date")

    # Variables météo de base
    lag_cols = ["Temperature_C", "Humidity_percent",
                "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"]
    df = add_lags(df, lag_cols, lags=[1, 3])

    # Nettoyer les NaN introduits par les lags
    df = df.dropna().reset_index(drop=True)

    # Sélection des features
    feature_cols = [
        c for c in df.columns
        if c not in ["date", "Temperature_C", "Humidity_percent", "Pressure_kPa", "Wind_m_s", "PRECTOTCORR"]
    ]
except Exception as e:
    print(f"❌ Erreur lors de la préparation des features : {e}")
    sys.exit(1)

# --------------------------
# 3) Split train / validation (70/15/15)
# --------------------------
try:
    train_size = int(len(df) * 0.7)
    val_size = int(len(df) * 0.15)

    train = df.iloc[:train_size]
    val = df.iloc[train_size:train_size + val_size]

    X_train = train[feature_cols]
    y_train_reg = train[["Temperature_C",
                         "Humidity_percent", "Pressure_kPa", "Wind_m_s"]]
    y_train_clf = (train["PRECTOTCORR"] > 1).astype(int)

    X_val = val[feature_cols]
    y_val_reg = val[["Temperature_C",
                     "Humidity_percent", "Pressure_kPa", "Wind_m_s"]]
    y_val_clf = (val["PRECTOTCORR"] > 1).astype(int)
except Exception as e:
    print(f"❌ Erreur lors du split train/val : {e}")
    sys.exit(1)

# --------------------------
# 4) Modèle de régression
# --------------------------
try:
    reg = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    reg.fit(X_train, y_train_reg.values)  # utiliser .values pour multi-output

    y_pred_reg = reg.predict(X_val)
    mae = mean_absolute_error(y_val_reg, y_pred_reg)
    r2 = r2_score(y_val_reg, y_pred_reg)

    print(f"🌡️ Régression - MAE: {mae:.2f}, R²: {r2:.2f}")
except Exception as e:
    print(f"❌ Erreur lors de l'entraînement du modèle de régression : {e}")
    sys.exit(1)

# --------------------------
# 5) Modèle de classification pluie
# --------------------------
try:
    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )
    calib_clf = CalibratedClassifierCV(clf, method="isotonic", cv=3)
    calib_clf.fit(X_train, y_train_clf)

    y_pred_clf = calib_clf.predict(X_val)
    y_prob_clf = calib_clf.predict_proba(X_val)[:, 1]

    acc = accuracy_score(y_val_clf, y_pred_clf)
    roc = roc_auc_score(y_val_clf, y_prob_clf)

    print(f"☔ Classification - Accuracy: {acc:.2f}, AUC: {roc:.2f}")
except Exception as e:
    print(f"❌ Erreur lors de l'entraînement du modèle de classification : {e}")
    sys.exit(1)

# --------------------------
# 6) Sauvegarde des modèles
# --------------------------
try:
    # Dossier du script actuel (backend/models)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Chemins complets des fichiers de sortie
    regressor_path = os.path.join(BASE_DIR, "MbulaCheck_regressor.pkl")
    classifier_path = os.path.join(BASE_DIR, "MbulaCheck_classifier.pkl")

    # Sauvegarde des modèles directement dans le même dossier
    save_model(reg, regressor_path)
    save_model(calib_clf, classifier_path)

    print("✅ Modèles sauvegardés dans le même dossier que le script :")
    print(f"   - {regressor_path}")
    print(f"   - {classifier_path}")

except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde des modèles : {e}")
    sys.exit(1)
