import streamlit as st
import pandas as pd

# Importiere deine eigenen Module
from src.extractors.crypto_api import get_crypto_data
from src.extractors.fred_api import get_fred_data
from src.extractors.weather_api import get_weather_data
from src.extractors.exchange_api import get_exchange_rate_data
from src.extractors.nasa_api import get_nasa_neo_data
from src.extractors.news_analyzer import get_news_and_analyze # <--- NEU: Unsere KI

# 1. Website-Setup
st.set_page_config(page_title="DataZeitgeist Dashboard", page_icon="📊", layout="wide")
st.title("📊 DataZeitgeist: Live Dashboard")
st.markdown("Analysiere und korreliere globale Datenströme in Echtzeit.")

# 2. Seitenleiste (Sidebar)
st.sidebar.header("⚙️ Steuerung")

dataset_options = {
    "Bitcoin Preis ($)": "crypto",
    "US-Zinsen (%)": "fred",
    "Wetter Berlin (°C)": "weather",
    "EUR/USD Wechselkurs": "exchange",
    "NASA Asteroiden": "nasa"
}

# Mapping für die KI-Suchanfragen
ai_queries = {
    "crypto": "Kryptowährung Bitcoin Markt",
    "fred": "US Notenbank Zinsen Wirtschaft",
    "exchange": "Euro Dollar Wechselkurs",
    "weather": None, # Bei Wetter und NASA lassen wir die KI erstmal weg
    "nasa": None
}

with st.sidebar.form("steuerung_form"):
    days = st.slider("Zeitraum (Tage)", min_value=7, max_value=90, value=30, step=7)
    
    st.subheader("Datenquellen vergleichen")
    ds1_name = st.selectbox("Datensatz 1", list(dataset_options.keys()), index=0)
    ds2_name = st.selectbox("Datensatz 2", list(dataset_options.keys()), index=1)
    
    submit_button = st.form_submit_button("Daten analysieren 🚀")

# 3. Daten-Ladefunktionen (mit Caching!)
@st.cache_data(ttl=3600)
def load_data(source, days):
    if source == "crypto": return get_crypto_data(coin_id="bitcoin", days=days)
    elif source == "fred": return get_fred_data(series_id="DGS10", days=days)
    elif source == "weather": return get_weather_data(city="Berlin", lat=52.52, lon=13.41, days=days)
    elif source == "exchange": return get_exchange_rate_data(base="EUR", target="USD", days=days)
    elif source == "nasa": return get_nasa_neo_data(days=days)
    return None

@st.cache_data(ttl=3600)
def load_ai_analysis(query):
    if not query: return None
    return get_news_and_analyze(query, "de", test_mode=False)

# 4. Magie: Ladebalken
if submit_button or ('df_merged' not in st.session_state): # Lädt auch beim ersten Seitenaufruf
    with st.spinner("Lade Live-Daten und KI-Analyse..."):
        src1 = dataset_options[ds1_name]
        src2 = dataset_options[ds2_name]
        
        df1 = load_data(src1, days)
        df2 = load_data(src2, days)
        
        # KI Analyse für den ersten Datensatz abrufen (falls verfügbar)
        ai_text = load_ai_analysis(ai_queries[src1])

    # 5. Daten zusammenführen & KPIs berechnen
    if df1 is not None and df2 is not None:
        df1 = df1.rename(columns={'Aufrufe': ds1_name})
        df2 = df2.rename(columns={'Aufrufe': ds2_name})
        
        df_merged = pd.merge(df1, df2, on='timestamp', how='inner').set_index('timestamp')
        
        st.markdown("---")
        
        # --- NEU: KPI BEREICH MIT METRIKEN UND KORRELATION ---
        st.subheader("📈 Key Performance Indicators (Heute vs. Vorwoche)")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Werte berechnen (Aktuell vs vor 7 Tagen)
        if len(df_merged) >= 7:
            val1_now = df_merged[ds1_name].iloc[-1]
            val1_old = df_merged[ds1_name].iloc[-7]
            delta1 = val1_now - val1_old
            
            val2_now = df_merged[ds2_name].iloc[-1]
            val2_old = df_merged[ds2_name].iloc[-7]
            delta2 = val2_now - val2_old
            
            # Mathematische Korrelation (Pearson)
            correlation = df_merged[ds1_name].corr(df_merged[ds2_name])
            
            with kpi1:
                # Formatierung je nach Datentyp anpassen
                format_str = "%.4f" if "Wechselkurs" in ds1_name else "%.2f"
                st.metric(label=ds1_name, value=format_str % val1_now, delta=format_str % delta1)
            with kpi2:
                format_str = "%.4f" if "Wechselkurs" in ds2_name else "%.2f"
                st.metric(label=ds2_name, value=format_str % val2_now, delta=format_str % delta2)
            with kpi3:
                # Interpretation der Korrelation
                if correlation > 0.7: corr_text = "Stark Positiv 🟢"
                elif correlation < -0.7: corr_text = "Stark Negativ 🔴"
                elif correlation > 0.3: corr_text = "Leicht Positiv ↗️"
                elif correlation < -0.3: corr_text = "Leicht Negativ ↘️"
                else: corr_text = "Kein Zusammenhang ⚪"
                
                st.metric(label="Statistische Korrelation (Pearson)", value=f"{correlation:.2f}", delta=corr_text, delta_color="off")
        
        st.markdown("---")
        
        # --- GRAPHEN BEREICH ---
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Verlauf: {ds1_name}**")
            st.line_chart(df_merged[ds1_name], color="#1DA1F2") 
        with col2:
            st.write(f"**Verlauf: {ds2_name}**")
            st.line_chart(df_merged[ds2_name], color="#FFD700")

        # --- NEU: KI ANALYSE BEREICH ---
        if ai_text:
            st.info(f"**🤖 Llama-3.1 KI-Analyse zu '{ds1_name}':**\n\n{ai_text}")

        # Rohdaten
        with st.expander("Tabelle mit Rohdaten anzeigen"):
            st.dataframe(df_merged, use_container_width=True)
    else:
        st.error("Fehler beim Laden der Daten. Bitte überprüfe die API-Keys in den Streamlit Settings.")
