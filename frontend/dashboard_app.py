import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
import plotly.express as px

# --- Configuration générale ---
st.set_page_config(
    page_title="MbulaCheck Dashboard",
    layout="wide",  # 🌍 Pleine largeur
    page_icon="🌦️"
)

# --- Style CSS personnalisé ---
st.markdown("""
    <style>
        .main {
            padding: 2rem 4rem;
            background-color: #f9fafc;
        }
        h1, h2, h3 {
            color: #1e3a8a;
        }
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            height: 3em;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }
        .timeline {
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Titre principal ---
st.title("🌦️ MbulaCheck Dashboard")

st.write("""
Welcome to **MbulaCheck**, your smart weather prediction dashboard for Kinshasa.  
Select a start date below to get a **7-day forecast** including temperature, wind, humidity, and rain probability.
""")

# --- Sélection de la date ---
start = st.date_input("📅 Select start date", value=date.today())
end = start + timedelta(days=6)
st.caption(f"Prediction period: **{start} → {end}**")

# --- Bouton ---
if st.button("🚀 Get 7-Day Forecast", use_container_width=True):
    st.info("Fetching predictions from MbulaCheck API...")
    url = "http://localhost:8000/predict/period"
    payload = {"start_date": str(start), "end_date": str(end)}

    try:
        resp = requests.post(url, json=payload)

        if resp.status_code == 200:
            df = pd.DataFrame(resp.json().get("results", []))

            if not df.empty:
                # Nettoyage des données
                df["Temperature_C"] = df["Temperature_C"].round(1)
                df["Humidity_percent"] = df["Humidity_percent"].round(1)
                df["Pressure_kPa"] = df["Pressure_kPa"].round(2)
                df["Wind_m_s"] = df["Wind_m_s"].round(2)
                df["Rain_Probability"] = (
                    df["Rain_Probability"] * 100).round(1)

                st.success("✅ 7-day forecast loaded successfully!")

                # --- Ligne de résumé rapide ---
                st.subheader("📊 Summary Overview")
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color:#000000FF;">🌡️ Avg Temp</h3>
                        <h2 style="color:#F97316;">{df['Temperature_C'].mean():.1f}°C</h2>
                    </div>
                """, unsafe_allow_html=True)
                col2.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color:#000000FF;">🌧️ Avg Rain Probability</h3>
                        <h2 style="color:#F97316;">{df['Rain_Probability'].mean():.1f}%</h2>
                    </div>
                """, unsafe_allow_html=True)
                col3.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color:#000000FF;">💨 Avg Wind</h3>
                        <h2 style="color:#F97316;">{df['Wind_m_s'].mean():.2f} m/s</h2>
                    </div>
                """, unsafe_allow_html=True)

                # --- Graphiques sur 2 colonnes ---
                st.markdown("### 📈 Weather Trends")
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**🌡️ Temperature (°C)**")
                    st.line_chart(df.set_index("date")[
                                  "Temperature_C"], use_container_width=True)

                    st.write("**💧 Humidity (%)**")
                    st.line_chart(df.set_index("date")[
                                  "Humidity_percent"], use_container_width=True)

                with col2:
                    st.write("**💨 Wind (m/s)**")
                    st.line_chart(df.set_index("date")[
                                  "Wind_m_s"], use_container_width=True)

                    st.write("**⏱ Pressure (kPa)**")
                    st.line_chart(df.set_index("date")[
                                  "Pressure_kPa"], use_container_width=True)

                # --- Timeline colorée ---
                st.markdown("### 🌦️ Rain Probability Timeline")
                fig = px.bar(
                    df,
                    x="date",
                    y="Rain_Probability",
                    color="Rain_Probability",
                    color_continuous_scale=["#4FC3F7", "#FFEB3B", "#FF7043"],
                    labels={
                        "Rain_Probability": "Rain Probability (%)", "date": "Date"},
                    title="Rain Probability over the Next 7 Days"
                )
                fig.update_layout(
                    template="plotly_white",
                    xaxis_title=None,
                    yaxis_title="Rain Probability (%)",
                    coloraxis_colorbar=dict(title="Rain %"),
                    bargap=0.3,
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- Tableau détaillé ---
                st.markdown("### 🧾 Detailed Forecast Table")
                st.dataframe(
                    df.rename(
                        columns={"Rain_Probability": "Rain_Probability (%)"}),
                    use_container_width=True
                )

                # --- Téléchargement ---
                st.markdown("### 📥 Download Results")
                st.download_button(
                    "Download as CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "mbulacheck_7day_forecast.csv",
                    "text/csv",
                    use_container_width=True
                )

            else:
                st.warning("⚠️ No prediction data available for this period.")
        else:
            st.error(f"API Error {resp.status_code}: {resp.text}")

    except Exception as e:
        st.error(f"❌ Could not connect to the API: {e}")

# --- Footer ---
st.markdown("""
<hr>
<p style='text-align:center; color:gray'>
Developed by <b>SkyLabs X</b> — Jordy Lubini, Ken Mwanza, James Kodila, Benally Kanangila 🌍  
</p>
""", unsafe_allow_html=True)
