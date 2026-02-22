import sys
import pandas as pd 
# WICHTIG: Die neue Summary-Funktion im Import hinzufügen!
from extractors.wikipedia_api import get_wikipedia_data, get_top_wikipedia_trend, get_wikipedia_summary
from visualizers.plotter import create_trend_chart
from publishers.social_poster import post_to_telegram
from publishers.social_poster import post_to_twitter

# === KONFIGURATION DER PLATTFORMEN ===
ENABLE_TELEGRAM = True
ENABLE_TWITTER = False
# =====================================

def generate_smart_caption(df, thema, summary):
    """Generiert einen dynamischen Text inkl. Beschreibung basierend auf den Daten."""
    thema_clean = thema.replace('_', ' ')
    hashtag_thema = "".join(word.capitalize() for word in thema_clean.split())
    
    # 1. Daten analysieren
    try:
        views_col = 'views' if 'views' in df.columns else df.columns[-1]
        
        if len(df) >= 14:
            recent_7_days = df[views_col].tail(7).mean()
            previous_7_days = df[views_col].iloc[-14:-7].mean()
            
            if previous_7_days > 0:
                change_percent = ((recent_7_days - previous_7_days) / previous_7_days) * 100
            else:
                change_percent = 0
            
            if change_percent > 20:
                trend_insight = f"📈 Starker Anstieg! Das Interesse stieg um {change_percent:.1f}%."
            elif change_percent < -20:
                trend_insight = f"📉 Der Hype flacht ab. Das Interesse sank um {abs(change_percent):.1f}%."
            elif change_percent > 0:
                trend_insight = f"↗️ Leichtes Wachstum (+{change_percent:.1f}%)."
            else:
                trend_insight = f"↘️ Leichter Rückgang (-{abs(change_percent):.1f}%)."
        else:
            trend_insight = "📊 Entwicklung der letzten 30 Tage."
            
    except Exception as e:
        print(f"⚠️ Fehler bei der Statistik: {e}")
        trend_insight = "📊 Entwicklung der letzten 30 Tage."

    # 2. Den fertigen Text zusammenbauen
    caption = f"🔍 Der tägliche Wikipedia-Trend!\n\n"
    caption += f"📌 Thema: {thema_clean}\n"
    
    # Wenn wir eine Zusammenfassung haben, fügen wir sie kursiv hinzu
    if summary:
        caption += f"ℹ️ Info: \"{summary}\"\n\n"
    else:
        caption += "\n"
        
    caption += f"{trend_insight}\n\n"
    caption += f"Was denkst du über diese Entwicklung?\n\n"
    caption += f"#{hashtag_thema} #Wikipedia #Trend"
    
    return caption

def main():
    print("🚀 Starte Daily Infographic Bot...")
    
    # Dynamisches Top-Thema holen
    thema = get_top_wikipedia_trend("de")
    
    # NEU: Wir holen uns die Beschreibung zum Thema!
    print("📚 Lade Kurzbeschreibung...")
    summary = get_wikipedia_summary(thema, "de")
    
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
    
    # WICHTIG: Die Summary übergeben wir jetzt an unsere Text-Funktion
    caption = generate_smart_caption(df, thema, summary)
    print(f"Generierter Text:\n{caption}\n")
    
    print("--- Starte Publishing-Phase ---")
    
    if ENABLE_TELEGRAM:
        post_to_telegram(chart_path, caption)
    else:
        print("⏭️ Telegram übersprungen.")

    if ENABLE_TWITTER:
        post_to_twitter(chart_path, caption)
    else:
        print("⏭️ Twitter übersprungen.")
        
    print("\n🎉 Pipeline erfolgreich komplett durchlaufen!")

if __name__ == "__main__":
    main()
