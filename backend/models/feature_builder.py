import pandas as pd
from utils import add_temporal_features, add_lags


def build_features_for_date(date_str, df_hist, lags=[1, 3]):
    """
    Prépare les features pour une date donnée à partir de l'historique météo.
    - date_str : '2024-06-23'
    - df_hist : DataFrame historique avec une colonne 'date' de type datetime
    - lags : liste d'entiers (délais en jours)
    """
    # Vérifier que la date cible et les jours précédents existent
    date = pd.to_datetime(date_str)
    needed_dates = [date - pd.Timedelta(days=lag) for lag in lags]
    for idx, d in enumerate(needed_dates):
        if d not in df_hist['date'].values:
            raise ValueError(
                f"Données manquantes pour le lag de {lags[idx]} jours avant {date_str} (besoin de {d.date()})")

    # Récupérer la ligne pour la date cible
    row = df_hist[df_hist['date'] == date].copy()
    if row.empty:
        raise ValueError(f"Aucune donnée pour la date {date_str}")

    # Ajout des features temporelles
    row = add_temporal_features(row, date_col='date')

    # Ajout des lags (sur une copie de l'historique, pour inclure les vraies valeurs des jours précédents)
    data_with_lags = pd.concat([df_hist, row], ignore_index=True)
    data_with_lags = add_lags(data_with_lags,
                              cols=["Temperature_C", "Humidity_percent",
                                    "Pressure_kPa", "Wind_m_s", "Precipitation_mm"],
                              lags=lags)

    # Après les lags, la dernière ligne est celle qui nous intéresse
    last_row = data_with_lags[data_with_lags['date'] == date]
    return last_row


def build_features_for_period(start_date, end_date, df_hist, lags=[1, 3]):
    """
    Prépare les features pour chaque jour d'une période.
    """
    period = pd.date_range(start=start_date, end=end_date)
    features = []
    for date in period:
        try:
            features.append(build_features_for_date(
                str(date.date()), df_hist, lags=lags))
        except Exception as e:
            print(f"⚠️ {e}")
    if features:
        return pd.concat(features, ignore_index=True)
    else:
        return pd.DataFrame()
