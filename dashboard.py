import streamlit as st
import pandas as pd

# Importiere deine eigenen Module aus dem src-Ordner!
from src.extractors.crypto_api import get_crypto_data
from src.extractors.fred_api import get_fred_data
from src.extractors.weather_api import get_weather_data
from src.extractors.exchange_api import get_exchange_rate_data
from src.extractors.nasa_api import get_nasa_neo_data

# 1. Website-Setup (Titel und Layout)
st.set_page_config(page_title="DataZeitgeist Dashboard", page_icon="📊", layout="wide")
st.title("📊 DataZeitgeist: Live Dashboard")
st.markdown("Willkommen in der interaktiven Daten-Zentrale. Wähle links deine Datenquellen aus, um sie zu analysieren.")

# 2. Seitenleiste (Sidebar) für Nutzer-Eingaben
st.sidebar.header("⚙️ Steuerung")
days = st.sidebar.slider("Zeitraum (Tage)", min_value=7, max_value=90, value=30)

dataset_options = {
    "Bitcoin Preis ($)": "crypto",
    "US-Zinsen (%)": "fred",
    "Wetter Berlin (°C)": "weather",
    "EUR/USD Wechselkurs": "exchange",
    "NASA Asteroiden": "nasa"
}

st.sidebar.subheader("Datenquellen vergleichen")
ds1_name = st.sidebar.selectbox("Datensatz 1", list(dataset_options.keys()), index=0)
ds2_name = st.sidebar.selectbox("Datensatz 2", list(dataset_options.keys()), index=1)

# 3. Daten laden (mit @st.cache_data, damit wir die APIs nicht bei jedem Klick neu abfragen!)
@st.cache_data(ttl=3600)
def load_data(source, days):
    if source == "crypto": return get_crypto_data(coin_id="bitcoin", days=days)
    elif source == "fred": return get_fred_data(series_id="DGS10", days=days)
    elif source == "weather": return get_weather_data(city="Berlin", lat=52.52, lon=13.41, days=days)
    elif source == "exchange": return get_exchange_rate_data(base="EUR", target="USD", days=days)
    elif source == "nasa": return get_nasa_neo_data(days=days)
    return None

# 4. Magie: Ladebalken anzeigen, während die Daten geholt werden
with st.spinner("Lade Live-Daten über APIs..."):
    df1 = load_data(dataset_options[ds1_name], days)
    df2 = load_data(dataset_options[ds2_name], days)

# 5. Daten zusammenführen und anzeigen
if df1 is not None and df2 is not None:
    # Umbenennen für den Plot
    df1 = df1.rename(columns={'Aufrufe': ds1_name})
    df2 = df2.rename(columns={'Aufrufe': ds2_name})
    
    # Pandas Merge
    df_merged = pd.merge(df1, df2, on='timestamp', how='inner').set_index('timestamp')

    st.markdown("---")
    st.subheader(f"Interaktive Analyse: {ds1_name} vs. {ds2_name}")
    
    # Layout mit zwei Spalten für unsere Graphen
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{ds1_name}**")
        # Streamlit zeichnet automatisch interaktive Graphen (Hover, Zoom etc.)
        st.line_chart(df_merged[ds1_name], color="#1DA1F2") 
        
    with col2:
        st.write(f"**{ds2_name}**")
        st.line_chart(df_merged[ds2_name], color="#FFD700")

    # Rohdaten als aufklappbare Tabelle
    with st.expander("Tabelle mit Rohdaten anzeigen"):
        st.dataframe(df_merged, use_container_width=True)
else:
    st.error("Fehler beim Laden der Daten. Bitte überprüfe die API-Keys.")
