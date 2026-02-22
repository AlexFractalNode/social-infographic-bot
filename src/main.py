import sys
from extractors.wikipedia_api import get_wikipedia_data
from visualizers.plotter import create_trend_chart
from publishers.social_poster import post_to_telegram
from publishers.social_poster import post_to_twitter

# === KONFIGURATION DER PLATTFORMEN ===
# Setze hier auf 'True' (aktivieren) oder 'False' (deaktivieren)
ENABLE_TELEGRAM = True
ENABLE_TWITTER = False
# =====================================

def main():
    print("🚀 Starte Daily Infographic Bot...")
    thema = "Künstliche_Intelligenz"
    
    # Phase 1: Extraktion
    df = get_wikipedia_data(thema, days=30)
    if df is None:
        print("❌ Abbruch in Phase 1.")
        return

    # Phase 2: Visualisierung
    chart_path = create_trend_chart(df, thema)
    if not chart_path:
        print("❌ Abbruch in Phase 2.")
        return
        
    # Phase 3: Publishing
    thema_clean = thema.replace('_', ' ')
    caption = f"📊 Der tägliche #Wikipedia Trend!\n\nSuchinteresse für '{thema_clean}' der letzten 30 Tage. Was denkst du über diese Entwicklung?\n\n#DataScience #Python #Automatisierung"
    
    print("\n--- Starte Publishing-Phase ---")
    
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
