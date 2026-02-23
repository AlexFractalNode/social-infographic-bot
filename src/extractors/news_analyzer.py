import os
import requests

def get_news_and_analyze(thema, language="de"):
    """
    Sucht aktuelle Nachrichten zum Thema und lässt die Groq KI den Grund für den Trend erklären.
    """
    print(f"📰 Suche nach dem 'Warum' für das Thema: {thema}...")
    
    # Keys aus GitHub Secrets laden
    gnews_key = os.getenv("GNEWS_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not gnews_key or not groq_key:
        print("⚠️ Warnung: GNews oder Groq API Keys fehlen. Überspringe News-Analyse.")
        return ""
        
    # Thema bereinigen (aus "Eric_Dane" wird "Eric Dane")
    query = thema.replace('_', ' ')
    
    # 1. Nachrichten über GNews suchen (Die Top 3 der aktuellsten Artikel)
    gnews_url = f"https://gnews.io/api/v4/search?q={query}&lang={language}&max=3&apikey={gnews_key}"
    
    try:
        news_response = requests.get(gnews_url, timeout=10)
        news_data = news_response.json()
        
        articles = news_data.get('articles', [])
        if not articles:
            print("ℹ️ Keine aktuellen Nachrichten zu diesem Thema gefunden.")
            return ""
            
        # Text für die KI zusammenbauen
        news_context = ""
        for i, article in enumerate(articles):
            news_context += f"{i+1}. {article['title']} - {article['description']}\n"
            
        # 2. KI analysieren lassen (via Groq)
        print("🧠 Lasse Groq KI (Llama 3) die Nachrichten analysieren...")
        
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        
        # Unser "Befehl" an die KI
        prompt = (
            f"Du bist ein Social Media Redakteur. Das Thema '{query}' trendet gerade extrem auf Wikipedia. "
            f"Hier sind die aktuellsten Schlagzeilen dazu:\n\n{news_context}\n\n"
            f"Fasse basierend auf diesen Schlagzeilen in maximal 2 kurzen, knackigen Sätzen zusammen, WARUM das Thema gerade trendet. "
            f"Schreibe es so, dass es direkt in einen Social Media Post passt (gerne mit 1 Emoji). "
            f"Antworte NUR mit den zwei Sätzen, ohne Einleitung, ohne Grußformel."
        )
        
        # Wir nutzen Llama 3 von Meta (rasend schnell und sehr intelligent)
        payload = {
            "model": "llama3-8b-8192", 
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        groq_response = requests.post(groq_url, headers=headers, json=payload, timeout=15)
        
        if groq_response.status_code == 200:
            groq_data = groq_response.json()
            ai_text = groq_data['choices'][0]['message']['content'].strip()
            
            # Falls die KI Anführungszeichen drum herum baut, entfernen wir sie
            if ai_text.startswith('"') and ai_text.endswith('"'):
                ai_text = ai_text[1:-1]
                
            print(f"✅ KI-Analyse erfolgreich: {ai_text}")
            return ai_text
        else:
            print(f"⚠️ Groq API Fehler: {groq_response.text}")
            return ""
            
    except Exception as e:
        print(f"⚠️ Fehler bei der News-Analyse: {e}")
        return ""
