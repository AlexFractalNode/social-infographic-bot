import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def create_trend_chart(df, thema):
    """
    Erstellt ein ansprechendes Liniendiagramm mit Trendlinie und Höchstwert-Markierung.
    """
    print("🎨 Generiere professionelle Grafik...")
    
    # Sicherstellen, dass das Output-Verzeichnis existiert
    os.makedirs("output", exist_ok=True)
    chart_path = "output/trend_chart.png"
    
    try:
        # Thema für den Titel aufbereiten
        thema_clean = thema.replace('_', ' ')
        
        # Sicherstellen, dass timestamp der Index ist (für einfaches Plotten)
        if 'timestamp' in df.columns:
            df = df.set_index('timestamp')
            
        # 1. Datenvorbereitung: 7-Tage-Trendlinie (Gleitender Durchschnitt) berechnen
        # min_periods=1 sorgt dafür, dass die Linie auch an den ersten Tagen gezeichnet wird
        df['Trend'] = df['Aufrufe'].rolling(window=7, min_periods=1).mean()
        
        # Den absoluten Höchstwert und das dazugehörige Datum finden
        max_views = df['Aufrufe'].max()
        max_date = df['Aufrufe'].idxmax()

        # 2. Design-Setup (Dunkles, modernes Theme)
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        
        # Hintergrundfarbe für den Plot-Bereich und die Figur anpassen
        bg_color = '#15202b' # Typisches Twitter/X Dark-Mode Blau-Grau
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        # Rasterlinien dezent im Hintergrund
        ax.grid(color='#38444d', linestyle='--', linewidth=0.5, alpha=0.7)

        # 3. Das eigentliche Plotten
        # Die nackten Zahlen als leicht transparente Fläche im Hintergrund
        ax.fill_between(df.index, df['Aufrufe'], color='#1DA1F2', alpha=0.2)
        ax.plot(df.index, df['Aufrufe'], color='#1DA1F2', linewidth=1.5, alpha=0.5, label='Tägliche Aufrufe')
        
        # Die geglättete Trendlinie prominent im Vordergrund
        ax.plot(df.index, df['Trend'], color='#FFD700', linewidth=3, label='7-Tage Trend')

        # 4. Den Höchstwert markieren (Pfeil & Text)
        # Formatiere die Zahl mit Tausendertrennzeichen (z.B. 250.000)
        max_views_str = f"{int(max_views):,}".replace(',', '.')
        
        ax.annotate(f'Peak: {max_views_str}',
                    xy=(max_date, max_views),
                    xytext=(10, 20), # Text leicht versetzt nach oben rechts
                    textcoords='offset points',
                    color='white',
                    fontweight='bold',
                    arrowprops=dict(arrowstyle="->", color='#FFD700', lw=1.5))

        # 5. Achsen und Titel formatieren
        plt.title(f'Wikipedia Trend: {thema_clean}', color='white', fontsize=16, fontweight='bold', pad=15)
        
        # Datumsformat auf der X-Achse (z.B. "15. Feb")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d. %b'))
        plt.xticks(rotation=45, color='#8899a6')
        plt.yticks(color='#8899a6')
        
        # Rahmenlinien (Spines) anpassen
        for spine in ax.spines.values():
            spine.set_color('#38444d')
            
        # Legende hinzufügen
        ax.legend(facecolor=bg_color, edgecolor='#38444d', labelcolor='white')

        # 6. Speichern und Aufräumen
        plt.tight_layout()
        plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        print(f"✅ Grafik erfolgreich gespeichert unter: {chart_path}")
        return chart_path
        
    except Exception as e:
        print(f"❌ Fehler bei der Grafikerstellung: {e}")
        return None
