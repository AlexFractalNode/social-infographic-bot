import sys
import time
import pandas as pd 

# --- Unsere Plugins (Extractors) ---
from extractors.wikipedia_api import get_wikipedia_data, get_top_wikipedia_trend, get_wikipedia_summary
from extractors.news_analyzer import get_news_and_analyze
from extractors.nasa_api import get_nasa_neo_data
from extractors.crypto_api import get_crypto_data
from extractors.weather_api import get_weather_data

# --- Engine Tools ---
from visualizers.plotter import create_trend_chart
from publishers.social_poster import post_to_telegram
from publishers.social_poster import post_to_twitter

# === CORE ENGINE KONFIGURATION ===
# Wähle hier das Modul für den heutigen Tag: "WIKIPEDIA" oder "NASA" oder "CRYPTO" oder "WEATHER"
ACTIVE_MODULE = "WEATHER"

ENABLE_TELEGRAM = True
ENABLE_TWITTER = False
TEST_MODE = False
# =====================================

def generate_smart_caption(df, thema, summary, ai_reason, source_name="Wikipedia"):
    """Generiert einen dynamischen Text, passend zur Datenquelle."""
    thema_clean = thema.replace('_', ' ')
    hashtag_thema = "".join(word.capitalize() for word in thema_clean.split())
    
    try:
        views_col = 'Aufrufe' if 'Aufrufe' in df.columns else df.columns[-1]
        if len(df) >= 14:
            recent_7_days = df[views_col].tail(7).mean()
            previous_7_days = df[views_col].iloc[-14:-7].mean()
            change_percent = ((recent_7_days - previous_7_days) / previous_7_days) * 100 if previous_7_days > 0 else 0
            
            if change_percent > 20: trend_insight = f"📈 Starker Anstieg! Die Zahlen stiegen um {change_percent:.1f}%."
            elif change_percent < -20: trend_insight = f"📉 Deutlicher Rückgang um {abs(change_percent):.1f}%."
            elif change_percent > 0: trend_insight = f"↗️ Leichtes Wachstum (+{change_percent:.1f}%)."
            else: trend_insight = f"↘️ Leichter Rückgang (-{abs(change_percent):.1f}%)."
        else:
            trend_insight = "📊 Entwicklung der letzten 30 Tage."
    except Exception:
        trend_insight = "📊 Entwicklung der letzten 30 Tage."

    # Text flexibel zusammenbauen
    caption = f"🪐 Der tägliche {source_name}-Datenpunkt!\n\n" if source_name == "NASA" else f"🔍 Der tägliche {source_name}-Trend!\n\n"
    caption += f"📌 Thema: {thema_clean}\n"
    
    if summary: caption += f"ℹ️ Info: \"{summary}\"\n\n"
    if ai_reason: caption += f"💡 Analyse:\n{ai_reason}\n\n"
        
    caption += f"{trend_insight}\n\n"
    caption += f"Was denkst du über diese Entwicklung?\n\n"
    caption += f"#{hashtag_thema} #{source_name} #DataScience"
    
    return caption

def main():
    print(f"🚀 Starte Data Engine... (Aktives Modul: {ACTIVE_MODULE})")
    if TEST_MODE: print("⚠️ TEST-MODUS AKTIV.")
    
    # --- VARIABLEN FÜR DIE ENGINE ---
    thema = ""
    summary = ""
    ai_reason = ""
    df = None
    source_name = ""
    y_label = ""
    
    # ==========================================
    # DATEN-ROUTING (Hier greifen die Plugins!)
    # ==========================================
    if ACTIVE_MODULE == "WIKIPEDIA":
        source_name = "Wikipedia"
        y_label = "Aufrufe"
        thema = get_top_wikipedia_trend("de")
        summary = get_wikipedia_summary(thema, "de")
        ai_reason = get_news_and_analyze(thema, "de", test_mode=TEST_MODE)
        time.sleep(2)
        df = get_wikipedia_data(thema, days=30)
        
    elif ACTIVE_MODULE == "NASA":
        source_name = "NASA"
        y_label = "Vorbeiflüge (NEOs)"
        thema = "Erdnahe Asteroiden"
        summary = "Das Center for Near Earth Object Studies (CNEOS) der NASA überwacht Kometen und Asteroiden, die sich der Umlaufbahn der Erde nähern."
        # Wir lassen die News-KI für NASA erstmal weg (daher leere Analyse)
        ai_reason = "" 
        df = get_nasa_neo_data(days=30)

    elif ACTIVE_MODULE == "CRYPTO":
        source_name = "Krypto"
        y_label = "Preis in USD ($)"
        thema = "Bitcoin"
        summary = "Bitcoin ist die weltweit erste und marktstärkste Kryptowährung, basierend auf einer dezentralen Blockchain-Technologie."
        # Wir lassen die KI die aktuellen Bitcoin-News analysieren!
        ai_reason = get_news_and_analyze("Bitcoin", "de", test_mode=TEST_MODE)
        df = get_crypto_data(coin_id="bitcoin", days=30)

    elif ACTIVE_MODULE == "WEATHER":
        source_name = "Umwelt/DWD"
        y_label = "Max. Temperatur (°C)"
        thema = "Klimatrend: Berlin"
        summary = "Die tägliche Höchsttemperatur in der Hauptstadt, basierend auf den Wettermodellen des Deutschen Wetterdienstes (DWD) via Open-Meteo."
        # Wir lassen die News-Analyse hier vorerst leer, da lokale Wetter-News oft schwer in 2 Sätzen zusammenzufassen sind.
        ai_reason = "" 
        df = get_weather_data(city="Berlin", lat=52.52, lon=13.41, days=30)
        
    else:
        print(f"❌ Unbekanntes Modul: {ACTIVE_MODULE}")
        return
    # ==========================================
    
    # --- AB HIER IST ALLES STANDARDISIERT ---
    if df is None or df.empty:
        print("❌ Abbruch: Keine Daten vom Plugin empfangen.")
        return

    # Plotter aufrufen (mit den dynamischen Labels!)
    chart_path = create_trend_chart(df, thema, source_name=source_name, y_label=y_label)
    if not chart_path: return
        
    print("\n--- Generiere Text ---")
    caption = generate_smart_caption(df, thema, summary, ai_reason, source_name)
    print(f"Generierter Text:\n{caption}\n")
    
    print("--- Publishing ---")
    if ENABLE_TELEGRAM: post_to_telegram(chart_path, caption)
    if ENABLE_TWITTER: post_to_twitter(chart_path, caption)
        
    print(f"\n🎉 Pipeline ({ACTIVE_MODULE}) erfolgreich durchlaufen!")

if __name__ == "__main__":
    main()
