import sys
import time
import pandas as pd 
from extractors.wikipedia_api import get_wikipedia_data, get_top_wikipedia_trend, get_wikipedia_summary
from visualizers.plotter import create_trend_chart
from publishers.social_poster import post_to_telegram
from publishers.social_poster import post_to_twitter
from extractors.news_analyzer import get_news_and_analyze

# === KONFIGURATION DER PLATTFORMEN ===
ENABLE_TELEGRAM = True
ENABLE_TWITTER = False
TEST_MODE = True # <--- NEUER SCHALTER: Auf 'True' setzen, um API-Kosten zu sparen!
# =====================================

def generate_smart_caption(df, thema, summary, ai_reason):
    """Generiert einen dynamischen Text inkl. Beschreibung und KI-Analyse."""
    thema_clean = thema.replace('_', ' ')
    hashtag_thema = "".join(word.capitalize() for word in thema_clean.split())
    
    try:
        views_col = 'Aufrufe' if 'Aufrufe' in df.columns else df.columns[-1]
        
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

    caption = f"🔍 Der tägliche Wikipedia-Trend!\n\n"
    caption += f"📌 Thema: {thema_clean}\n"
    
    if summary:
        caption += f"ℹ️ Info: \"{summary}\"\n\n"
        
    if ai_reason:
        caption += f"💡 Warum trendet das gerade?\n{ai_reason}\n\n"
        
    caption += f"{trend_insight}\n\n"
    caption += f"Was denkst du über diese Entwicklung?\n\n"
    caption += f"#{hashtag_thema} #Wikipedia #Trend"
    
    return caption

def main():
    if TEST_MODE:
        print("⚠️ HINWEIS: Der Test-Modus ist aktiv. Externe Bezahl-APIs werden übersprungen.")
        
    print("🚀 Starte Daily Infographic Bot...")
    
    thema = get_top_wikipedia_trend("de")
    
    print("📚 Lade Kurzbeschreibung...")
    summary = get_wikipedia_summary(thema, "de")
    
    # NEU: Wir übergeben den Test-Modus an die Analyse-Funktion
    ai_reason = get_news_and_analyze(thema, "de", test_mode=TEST_MODE)
    
    print("⏳ Warte 2 Sekunden (Wikipedia Spam-Schutz)...")
    time.sleep(2)
    
    df = get_wikipedia_data(thema, days=30)
    if df is None or df.empty:
        print("❌ Abbruch in Phase 1: Daten konnten nicht geladen werden.")
        return

    chart_path = create_trend_chart(df, thema)
    if not chart_path:
        print("❌ Abbruch in Phase 2.")
        return
        
    print("\n--- Generiere smarten Text ---")
    caption = generate_smart_caption(df, thema, summary, ai_reason)
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
