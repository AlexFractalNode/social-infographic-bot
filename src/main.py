import sys
# Falls pandas hier noch nicht importiert war, fügen wir es sicherheitshalber hinzu
import pandas as pd 
from extractors.wikipedia_api import get_wikipedia_data, get_top_wikipedia_trend
from visualizers.plotter import create_trend_chart
from publishers.social_poster import post_to_telegram
from publishers.social_poster import post_to_twitter

# === KONFIGURATION DER PLATTFORMEN ===
ENABLE_TELEGRAM = True
ENABLE_TWITTER = False
# =====================================

def generate_smart_caption(df, thema):
    """Generiert einen dynamischen Text basierend auf den Daten im DataFrame."""
    # 1. Thema säubern und dynamischen Hashtag bauen
    thema_clean = thema.replace('_', ' ')
    # Aus "Eric Dane" wird "EricDane" für den Hashtag
    hashtag_thema = "".join(word.capitalize() for word in thema_clean.split())
    
    try:
        # 2. Daten analysieren (Wir suchen die Spalte mit den Aufrufen)
        # Meistens heißt sie 'views', ansonsten nehmen wir die letzte Spalte
        views_col = 'views' if 'views' in df.columns else df.columns[-1]
        
        # Berechne den Durchschnitt der letzten 7 Tage vs. die 7 Tage davor
        if len(df) >= 14:
            recent_7_days = df[views_col].tail(7).mean()
            previous_7_days = df[views_col].iloc[-14:-7].mean()
            
            # Prozentualen Anstieg/Abfall berechnen
            if previous_7_days > 0:
                change_percent = ((recent_7_days - previous_7_days) / previous_7_days) * 100
            else:
                change_percent = 0
            
            # 3. Den passenden Satz zum Trend auswählen
            if change_percent > 20:
                trend_insight = f"📈 Starker Anstieg! Das Interesse ist in den letzten 7 Tagen um {change_percent:.1f}% im Vergleich zur Vorwoche gestiegen."
            elif change_percent < -20:
                trend_insight = f"📉 Der Hype flacht ab. Das Interesse sank zuletzt um {abs(change_percent):.1f}%."
            elif change_percent > 0:
                trend_insight = f"↗️ Leichtes Wachstum. Das Interesse stieg zuletzt um {change_percent:.1f}%."
            else:
                trend_insight = f"↘️ Leichter Rückgang. Das Interesse sank um {abs(change_percent):.1f}%."
        else:
            trend_insight = "📊 Hier ist die Entwicklung der Aufrufe."
            
    except Exception as e:
        print(f"⚠️ Konnte keine erweiterten Statistiken berechnen: {e}")
        trend_insight = "📊 Hier ist die Entwicklung der letzten 30 Tage."

    # 4. Den fertigen Text zusammenbauen (ohne DataScience Hashtags!)
    caption = (
        f"🔍 Der tägliche Wikipedia-Trend!\n\n"
        f"Thema: {thema_clean}\n"
        f"{trend_insight}\n\n"
        f"Was denkst du über diese Entwicklung?\n\n"
        f"#{hashtag_thema} #Wikipedia #Trend"
    )
    return caption

def main():
    print("🚀 Starte Daily Infographic Bot...")
    
    # Dynamisches Top-Thema holen
    thema = get_top_wikipedia_trend("de")
    
    # Phase 1: Extraktion
    df = get_wikipedia_data(thema, days=30)
    if df is None or df.empty:
        print("❌ Abbruch in Phase 1.")
        return

    # Phase 2: Visualisierung
    chart_path = create_trend_chart(df, thema)
    if not chart_path:
        print("❌ Abbruch in Phase 2.")
        return
        
    # Phase 3: Publishing
    print("\n--- Generiere smarten Text ---")
    
    # Hier rufen wir unsere neue smarte Funktion auf!
    caption = generate_smart_caption(df, thema)
    print(f"Generierter Text:\n{caption}\n")
    
    print("--- Starte Publishing-Phase ---")
    
    # Telegram Steuerung
    if ENABLE_TELEGRAM:
        post_to_telegram(chart_path, caption)
    else:
        print("⏭️ Telegram-Post übersprungen (in Konfiguration deaktiviert).")

    # Twitter/X Steuerung
    if ENABLE_TWITTER:
        post_to_twitter(chart_path, caption)
    else:
        print("⏭️ Twitter-Post übersprungen (in Konfiguration deaktiviert).")
        
    print("\n🎉 Pipeline erfolgreich komplett durchlaufen!")

if __name__ == "__main__":
    main()
