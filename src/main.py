import sys
from extractors.wikipedia_api import get_wikipedia_data

def main():
    print("🚀 Starte Daily Infographic Bot...")
    
    # Phase 1: Daten extrahieren
    thema = "Künstliche_Intelligenz"
    df = get_wikipedia_data(thema, days=30)
    
    if df is not None:
        print("✅ Erfolgreich extrahiert. Zeige die letzten 5 Tage:")
        print(df.tail())
        print("🎉 Phase 1 (Extraction) ist abgeschlossen!")
    else:
        print("❌ Pipeline abgebrochen, da keine Daten geladen wurden.")

if __name__ == "__main__":
    main()
