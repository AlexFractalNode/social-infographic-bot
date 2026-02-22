import requests
import pandas as pd
from datetime import datetime, timedelta

def get_top_wikipedia_trend(language="de"):
    """
    Holt den am meisten aufgerufenen echten Wikipedia-Artikel von gestern.
    """
    print(f"🔍 Suche nach dem Top-Trend von gestern ({language}.wikipedia)...")
    
    # Wir brauchen das Datum von gestern im Format YYYY/MM/DD
    yesterday = datetime.utcnow() - timedelta(days=1)
    date_str = yesterday.strftime('%Y/%m/%d')
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{language}.wikipedia/all-access/{date_str}"
    
    headers = {
        "User-Agent": "WikiTrendBot/1.0 (https://github.com/AlexFractalNode/social-infographic-bot)"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Fehler bei der API-Abfrage der Trends: {response.status_code}")
        return "Künstliche_Intelligenz" # Fallback, falls die API mal streikt
        
    data = response.json()
    articles = data['items'][0]['articles']
    
    # Diese Begriffe wollen wir ignorieren, da es keine "echten" Themen sind
    ignored_titles = [
        "Hauptseite", "Wikipedia:Hauptseite", "Spezial:Suche", 
        "Spezial:Anmelden", "Wikipedia:Impressum", "Wikipedia:Datenschutz",
        "Cleopatra", # Oft durch System-Tests verfälscht
        "Wikipedia:Über_Wikipedia", "-_Hauptseite"
    ]
    
    # Gehe die Liste von oben nach unten durch und nimm das erste echte Thema
    for article in articles:
        title = article['article']
        # Prüfen, ob der Titel in der Ignorier-Liste ist oder mit "Spezial:" / "Wikipedia:" anfängt
        if title not in ignored_titles and not title.startswith(("Spezial:", "Wikipedia:", "Datei:")):
            print(f"🌟 Top-Trend gefunden: {title} ({article['views']} Aufrufe)")
            return title
            
    return "Künstliche_Intelligenz" # Fallback

def get_wikipedia_data(article, days=30, language="de.wikipedia.org"):
    """Holt die Wikipedia-Aufrufzahlen und gibt ein Pandas DataFrame zurück."""
    print(f"📡 Lade Daten für: {article}...")
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{language}/all-access/all-agents/{article}/daily/{start_str}/{end_str}"

    # WICHTIG: Passe die E-Mail hier an!
    headers = {
        "User-Agent": "ZeitgeistBot_StudentProject/1.0 (lewiv59587@amiralty.com)"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Fehler: API antwortet mit Status {response.status_code}")
        return None

    data = response.json()
    df = pd.DataFrame(data['items'])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H')
    df = df[['timestamp', 'views']]
    df.columns = ['Datum', 'Aufrufe']
    df.set_index('Datum', inplace=True)

    def get_wikipedia_summary(title, language="de"):
    """
    Holt die Kurzbeschreibung (den ersten Absatz) eines Wikipedia-Artikels.
    """
    url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}"
    headers = {
        "User-Agent": "WikiTrendBot/1.0 (https://github.com/AlexFractalNode/social-infographic-bot)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # 'extract' enthält den reinen Text ohne HTML
            summary = data.get("extract", "")
            
            # Text kürzen, falls er für Telegram/Twitter zu lang ist
            if len(summary) > 180:
                summary = summary[:177] + "..."
            return summary
    except Exception as e:
        print(f"⚠️ Konnte Zusammenfassung für {title} nicht laden: {e}")
        
    return ""
    return df
