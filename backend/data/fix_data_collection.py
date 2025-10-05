import requests
import pandas as pd
import os

def collect_weather_data_fixed():
    """Collecte des données météorologiques avec la bonne structure"""
    
    # Configuration
    LATITUDE = -4.4419   # Kinshasa
    LONGITUDE = 15.2663
    START_YEAR = 2018
    END_YEAR = 2024
    PARAMETERS = ["T2M", "RH2M", "PRECTOT", "WS2M", "PS"]
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        print(f"📥 Collecte des données {year}...")
        
        start = f"{year}0101"
        end = f"{year}1231"
        params_str = ",".join(PARAMETERS)
        
        url = (
            f"{base_url}?start={start}&end={end}"
            f"&latitude={LATITUDE}&longitude={LONGITUDE}"
            f"&parameters={params_str}"
            f"&format=JSON&community=RE"
        )
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                if "properties" in data and "parameter" in data["properties"]:
                    records = data["properties"]["parameter"]
                    
                    # Créer un DataFrame pour chaque paramètre
                    for param, values in records.items():
                        df_param = pd.DataFrame({
                            'date': pd.to_datetime(list(values.keys()), format='%Y%m%d'),
                            'parameter': param,
                            'value': list(values.values())
                        })
                        all_data.append(df_param)
                        
        except Exception as e:
            print(f"⚠️ Erreur pour {year}: {e}")
            continue
    
    if not all_data:
        print("❌ Aucune donnée collectée !")
        return
    
    # Combiner toutes les données
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Pivoter pour avoir une colonne par paramètre
    df_pivot = combined_df.pivot(index='date', columns='parameter', values='value')
    df_pivot = df_pivot.reset_index()
    
    # Nettoyer les données
    df_pivot = df_pivot.replace(-999.0, pd.NA).dropna()
    
    # Renommer les colonnes
    df_pivot = df_pivot.rename(columns={
        "T2M": "Temperature_C",
        "RH2M": "Humidity_percent",
        "PRECTOT": "Precipitation_mm", 
        "WS2M": "Wind_m_s",
        "PS": "Pressure_kPa"
    })
    
    # Sauvegarder
    output_file = "data/nasa_weather.csv"
    df_pivot.to_csv(output_file, index=False)
    
    print(f"✅ Données sauvegardées dans {output_file}")
    print(f"📊 Shape: {df_pivot.shape}")
    print(f"📅 Période: {df_pivot['date'].min()} → {df_pivot['date'].max()}")
    print("\n📋 Aperçu des données:")
    print(df_pivot.head())
    print("\n📋 Colonnes disponibles:")
    print(df_pivot.columns.tolist())
    
    return df_pivot

if __name__ == "__main__":
    collect_weather_data_fixed()
