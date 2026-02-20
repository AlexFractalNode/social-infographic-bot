import os
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
