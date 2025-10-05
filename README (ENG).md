# MbulaCheck API 🌦️ — Quick Start & Usage Guide

**MbulaCheck** is a FastAPI-based REST API developed by SkyLabs X for predicting weather (temperature, humidity, pressure, wind, rain probability) in Kinshasa (DRC), using models trained on NASA Earth data from 2018 to 2025. You can request predictions for a specific date or for a range of dates (a period).

---

## 👨‍💻 Developed by

**SkyLabs X Team**  
- Jordy Lubini  
- Ken Mwanza  
- James Kodila  
- Benally Kanangila

---

## 🌍 Project Demo

🎥 **Watch the 30-second demo video here:**  
👉 [https://drive.google.com/file/d/1zptkjsKWz670qRp0Irmw-11KdnGEwhWj/view?usp=sharing](https://drive.google.com/file/d/1zptkjsKWz670qRp0Irmw-11KdnGEwhWj/view?usp=sharing)

*(Accessible publicly — no login required)*

---

## 🚀 Getting Started

### 1. Start the API

Make sure you have:

- The trained models saved as `models/MbulaCheck_regressor.pkl` and `models/MbulaCheck_classifier.pkl`
- The weather history as `data/nasa_weather_2018_2025.csv`

Then run:

```bash
uvicorn main:app --reload
```

Visit the interactive docs at:  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## Main Endpoints

### 1. Predict Weather for a Period

**POST** `/predict/period`

**Description**: Returns daily weather predictions for the specified period.

**Sample JSON Request:**

```json
{
  "start_date": "2024-06-01",
  "end_date": "2024-06-07"
}
```

**Sample Response:**

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

### 2. Download Results (CSV or JSON)

**GET** `/download`

**Query Parameters:**

- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `format`: `csv` or `json` (default: csv)

**Example for CSV:**

```
/download?start_date=2024-06-01&end_date=2024-06-07&format=csv
```

**Example for JSON:**

```
/download?start_date=2024-06-01&end_date=2024-06-07&format=json
```

---

### 3. Get Period Statistics

**GET** `/period/stats`

**Query Parameters:**

- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Sample Response:**

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

## Example: Using the API with Python

```python
import requests

# Predict for a period
resp = requests.post(
    "http://localhost:8000/predict/period",
    json={"start_date": "2024-06-01", "end_date": "2024-06-07"}
)
print(resp.json())

# Download results as CSV
resp = requests.get(
    "http://localhost:8000/download",
    params={"start_date": "2024-06-01", "end_date": "2024-06-07", "format": "csv"}
)
with open("results.csv", "wb") as f:
    f.write(resp.content)

# Get statistics
resp = requests.get(
    "http://localhost:8000/period/stats",
    params={"start_date": "2024-06-01", "end_date": "2024-06-07"}
)
print(resp.json())
```

---

## Notes

- The API works for dates for which historical weather data is available.
- The models are trained for Kinshasa. (Prototype: can be extended to other locations if you provide historical data.)
- Data source: NASA POWER.
- Returned variables: temperature (`°C`), humidity (`%`), pressure (`kPa`), wind speed (`m/s`), rain probability (0-1).

---

## 📧 Contact

For questions or suggestions, reach out at: [jordylubini64@gmail.com]

## 📎 Project Repository
👉 https://github.com/Master-2290/MbulaCheck



