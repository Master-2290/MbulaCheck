# MbulaCheck API 🌦️ — Documentation d’Utilisation

**MbulaCheck** est une API FastAPI développée par SkyLabs X qui permet de prédire la météo (température, humidité, pression, vent, probabilité de pluie) à Kinshasa à partir d’une date ou d’une période, en utilisant des modèles entraînés sur des données NASA.

## **Développé par : Jordy Lubini, Ken Mwanza, James Kodila, Kanangila Benally — membres de SkyLabs X**

## 🚀 Démarrage rapide

### 1. Lancer l’API

Assurez-vous d’avoir :

- Les modèles entraînés dans `models/MbulaCheck_regressor.pkl` et `models/MbulaCheck_classifier.pkl`
- L’historique météo dans `data/nasa_weather.csv`

```bash
uvicorn main:app --reload
```

Accédez à la documentation interactive sur :  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📚 Endpoints principaux

### 1. Prédiction météo sur une période

**POST** `/predict/period`

**Description** : Retourne les prédictions météo pour chaque jour de la période.

**Body JSON exemple :**

```json
{
  "start_date": "2024-06-01",
  "end_date": "2024-06-07"
}
```

**Réponse exemple :**

```json
{
  "results": [
    {
      "date": "2024-06-01",
      "Temperature_C": 27.5,
      "Humidity_percent": 80.1,
      "Pressure_kPa": 101.2,
      "Wind_m_s": 2.1,
      "Rain_Probability": 0.31
    },
    ...
  ]
}
```

---

### 2. Télécharger les résultats (CSV ou JSON)

**GET** `/download`

**Paramètres URL :**

- `start_date` : date début (YYYY-MM-DD)
- `end_date` : date fin (YYYY-MM-DD)
- `format` : `csv` ou `json` (défaut : csv)

**Exemple pour CSV :**

```
/download?start_date=2024-06-01&end_date=2024-06-07&format=csv
```

**Exemple pour JSON :**

```
/download?start_date=2024-06-01&end_date=2024-06-07&format=json
```

---

### 3. Statistiques sur la période

**GET** `/period/stats`

**Paramètres URL :**

- `start_date` : date début (YYYY-MM-DD)
- `end_date` : date fin (YYYY-MM-DD)

**Réponse exemple :**

```json
{
  "Temperature_C_mean": 26.7,
  "Temperature_C_max": 29.5,
  "Temperature_C_min": 24.1,
  "Humidity_percent_mean": 81.2,
  "Pressure_kPa_mean": 101.3,
  "Wind_m_s_mean": 2.2,
  "Nb_days_rain_proba_gt_0.6": 2
}
```

---

## 🎯 Exemple d’utilisation avec Python

```python
import requests

# Prédiction sur une période
resp = requests.post(
    "http://localhost:8000/predict/period",
    json={"start_date": "2024-06-01", "end_date": "2024-06-07"}
)
print(resp.json())

# Télécharger en CSV
resp = requests.get(
    "http://localhost:8000/download",
    params={"start_date": "2024-06-01", "end_date": "2024-06-07", "format": "csv"}
)
with open("resultats.csv", "wb") as f:
    f.write(resp.content)

# Statistiques
resp = requests.get(
    "http://localhost:8000/period/stats",
    params={"start_date": "2024-06-01", "end_date": "2024-06-07"}
)
print(resp.json())
```

---

## 🗒️ Notes

- L’API fonctionne pour les dates où l’historique météo est disponible.
- Les modèles sont adaptés à Kinshasa (prototype : extension possible à d’autres villes avec un historique ad hoc).
- Sources de données : NASA POWER.
- Variables retournées : température (`°C`), humidité (`%`), pression (`kPa`), vent (`m/s`), probabilité de pluie (0-1).

---

## 📧 Contact

Pour toute question ou suggestion, contactez : [jordylubini64@gmail.com]
