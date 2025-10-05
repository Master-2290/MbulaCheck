import requests
import pandas as pd
import os

# --------------------------
# CONFIGURATION
# --------------------------
LATITUDE = -4.4419  # Kinshasa
LONGITUDE = 15.2663  # Kinshasa
START_YEAR = 2018
END_YEAR = 2024  # inclus

# Variables météo à récupérer
# T2M : Température 2m (°C)
# RH2M : Humidité relative (%)
# PRECTOT : Précipitations (mm/jour)
# WS2M : Vitesse du vent à 2m (m/s)
# PS : Pression de surface (kPa)
PARAMETERS = ["T2M", "RH2M", "PRECTOT", "WS2M", "PS"]

OUTPUT_DIR = "data/raw"
FINAL_FILE = "data/nasa_weather.csv"

# --------------------------
# COLLECTE DES DONNÉES NASA POWER (journalier)
# --------------------------


def collect_nasa_data(lat, lon, start, end, params):
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params_str = ",".join(params)

    url = (
        f"{base_url}?start={start}&end={end}"
        f"&latitude={lat}&longitude={lon}"
        f"&parameters={params_str}"
        f"&format=JSON&community=RE"
    )

    print(f"🌐 Requête API: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Erreur API: {response.status_code}")

    data = response.json()

    if "properties" not in data or "parameter" not in data["properties"]:
        print(f"❌ Données invalides reçues: {data}")
        return pd.DataFrame()

    records = data["properties"]["parameter"]

    # Transformation en DataFrame - structure correcte
    df = pd.DataFrame(records).transpose()
    df.index = pd.to_datetime(df.index, format="%Y%m%d", errors='coerce')
    df = df.reset_index()
    df.rename(columns={'index': 'date'}, inplace=True)

    # Restructurer les données pour avoir une ligne par date
    df_melted = df.melt(
        id_vars=['date'], var_name='parameter', value_name='value')
    df_pivot = df_melted.pivot(
        index='date', columns='parameter', values='value')
    df_pivot = df_pivot.reset_index()

    return df_pivot

# --------------------------
# PIPELINE DE COLLECTE SUR N ANNÉES
# --------------------------


def get_dataset(lat, lon, start_year, end_year, params):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_data = []

    for year in range(start_year, end_year + 1):
        yearly_file = os.path.join(OUTPUT_DIR, f"nasa_{year}.csv")

        # Vérifier si les données sont déjà collectées
        if os.path.exists(yearly_file):
            print(f"✅ Chargement local des données {year}...")
            df = pd.read_csv(yearly_file, index_col=0, parse_dates=True)
        else:
            print(f"📥 Collecte des données {year}...")
            start = f"{year}0101"
            end = f"{year}1231"

            try:
                df = collect_nasa_data(lat, lon, start, end, params)
                if not df.empty:
                    df.to_csv(yearly_file)  # sauvegarde locale
                    print(f"💾 Données sauvegardées: {yearly_file}")
            except Exception as e:
                print(f"⚠️ Erreur collecte {year}: {e}")
                continue

        if df is not None and not df.empty:
            all_data.append(df)

    if not all_data:
        raise ValueError("Aucune donnée collectée !")

    dataset = pd.concat(all_data)
    dataset = dataset.sort_index()

    # Nettoyage des données
    dataset = dataset.replace(-999.0, pd.NA).dropna()

    print(f"📊 Dataset final: {dataset.shape}")
    print(f"📅 Période: {dataset.index.min()} → {dataset.index.max()}")

    return dataset


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    dataset = get_dataset(LATITUDE, LONGITUDE,
                          START_YEAR, END_YEAR, PARAMETERS)

    # Renommer les colonnes pour plus de clarté
    dataset = dataset.rename(columns={
        "T2M": "Temperature_C",
        "RH2M": "Humidity_percent",
        "PRECTOT": "Precipitation_mm",
        "WS2M": "Wind_m_s",
        "PS": "Pressure_kPa"
    })

    # Sauvegarde du dataset final
    dataset.to_csv(FINAL_FILE, index=True)
    print(f"✅ Données consolidées sauvegardées dans {FINAL_FILE}")
    print(dataset.head())
