import os
import tweepy
import requests

def post_to_telegram(image_path, caption):
    """Sendet ein Bild mit Text an einen Telegram-Chat."""
    print("📲 Bereite Telegram-Post vor...")
    
    # Secrets aus der Umgebung abrufen (werden von GitHub Actions reingereicht)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Fehler: Telegram Secrets (Token oder Chat ID) fehlen!")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    
    try:
        with open(image_path, 'rb') as image_file:
            payload = {"chat_id": chat_id, "caption": caption}
            files = {"photo": image_file}
            
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                print("✅ Erfolgreich an Telegram gesendet!")
                return True
            else:
                print(f"❌ Telegram API Fehler: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        return False


def post_to_twitter(image_path, caption):
    """Sendet ein Bild mit Text an Twitter/X."""
    print("🐦 Bereite Twitter-Post vor...")
    
    # Secrets laden
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ Fehler: Twitter Secrets fehlen!")
        return False
        
    try:
        # 1. Authentifizierung für den Medien-Upload (benötigt die alte v1.1 API)
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api_v1 = tweepy.API(auth)
        
        # 2. Authentifizierung für den Tweet selbst (neue v2 API)
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        # Bild hochladen
        print("⏳ Lade Bild auf Twitter hoch...")
        media = api_v1.media_upload(image_path)
        
        # Tweet mit Bild senden
        print("⏳ Sende Tweet...")
        response = client.create_tweet(text=caption, media_ids=[media.media_id])
        
        print(f"✅ Erfolgreich getwittert! Tweet ID: {response.data['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Twittern: {e}")
        return False
