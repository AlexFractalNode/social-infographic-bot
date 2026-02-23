import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Ein gemeinsamer, sauberer Header für alle Anfragen. 
# Wikipedia blockiert Skripte ohne diesen Header extrem schnell!
HEADERS = {
    "User-Agent": "WikiTrendBot/1.1 (https://github.com/AlexFractalNode/social-infographic-bot; bot@example.com)"
}

def get_top_wikipedia_trend(language="de"):
    """Holt den am meisten aufgerufenen Wikipedia-Artikel."""
    print(f"🔍 Suche nach dem Top-Trend ({language}.wikipedia)...")
    
    # Wir probieren erst gestern (1), dann vorgestern (2), falls Wikipedia noch nicht fertig ist
    for days_back in [1, 2]:
        target_date = datetime.utcnow() - timedelta(days=days_back)
        date_str = target_date.strftime('%Y/%m/%d')
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{language}.wikipedia/all-access/{date_str}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data['items'][0]['articles']
                
                ignored_titles = [
                    "Hauptseite", "Wikipedia:Hauptseite", "Spezial:Suche", 
                    "Spezial:Anmelden", "Wikipedia:Impressum", "Wikipedia:Datenschutz",
                    "Cleopatra", "Wikipedia:Über_Wikipedia", "-_Hauptseite"
                ]
                
                for article in articles:
                    title = article['article']
                    if title not in ignored_titles and not title.startswith(("Spezial:", "Wikipedia:", "Datei:")):
                        print(f"🌟 Top-Trend gefunden für {date_str}: {title}")
                        return title
            else:
                print(f"⚠️ Trend-Daten für {date_str} noch nicht da (HTTP {response.status_code}). Versuche vorherigen Tag...")
        except Exception as e:
            print(f"⚠️ Fehler bei der Verbindung: {e}")
            
        time.sleep(1) # Kurze Pause vor dem nächsten Versuch

    print("❌ Keine Trends gefunden. Nutze Fallback.")
    return "Künstliche_Intelligenz"

def get_wikipedia_summary(title, language="de"):
    """Holt die Kurzbeschreibung (den ersten Absatz) eines Wikipedia-Artikels."""
    url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}"
    
    try:
        time.sleep(1) # Pause für den Spam-Schutz
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = data.get("extract", "")
            if len(summary) > 180:
                summary = summary[:177] + "..."
            return summary
    except Exception as e:
        print(f"⚠️ Konnte Zusammenfassung für {title} nicht laden: {e}")
        
    return ""

def get_wikipedia_data(title, language="de", days=30):
    """Holt die täglichen Aufrufzahlen für einen bestimmten Artikel."""
    print(f"📊 Lade Aufruf-Daten für: {title}...")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Format für die API: YYYYMMDD00
    start_str = start_date.strftime('%Y%m%d00')
    end_str = end_date.strftime('%Y%m%d00')
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{language}.wikipedia/all-access/all-agents/{title}/daily/{start_str}/{end_str}"
    
    try:
        time.sleep(2) # Wichtigste Pause, bevor wir die große Tabelle holen
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if not items:
                print("❌ API hat keine Datenpunkte zurückgegeben.")
                return None
                
            df = pd.DataFrame(items)
            # Wir behalten nur das Wichtigste für den Graphen
            if 'timestamp' in df.columns and 'views' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H').dt.date
                return df[['timestamp', 'views']]
            else:
                return df
        else:
            print(f"❌ API-Fehler bei den Daten: HTTP {response.status_code}")
            print(f"Details: {response.text[:150]}") # Zeigt an, WARUM Wikipedia blockt
            return None
    except Exception as e:
        print(f"❌ Verbindungsfehler beim Datenladen: {e}")
        return None
