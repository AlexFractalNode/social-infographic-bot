import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# NEU: source_name und y_label hinzugefügt!
def create_trend_chart(df, thema, source_name="Wikipedia", y_label="Aufrufe"):
    """
    Erstellt ein ansprechendes Liniendiagramm mit Trendlinie und Höchstwert-Markierung.
    """
    print(f"🎨 Generiere professionelle Grafik für {source_name}...")
    
    os.makedirs("output", exist_ok=True)
    chart_path = "output/trend_chart.png"
    
    try:
        thema_clean = thema.replace('_', ' ')
        
        if 'timestamp' in df.columns:
            df = df.set_index('timestamp')
            
        df['Trend'] = df['Aufrufe'].rolling(window=7, min_periods=1).mean()
        
        max_views = df['Aufrufe'].max()
        max_date = df['Aufrufe'].idxmax()

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        
        bg_color = '#15202b'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        ax.grid(color='#38444d', linestyle='--', linewidth=0.5, alpha=0.7)

        ax.fill_between(df.index, df['Aufrufe'], color='#1DA1F2', alpha=0.2)
        # NEU: Das Label in der Legende passt sich jetzt an (z.B. "Tägliche Vorbeiflüge")
        ax.plot(df.index, df['Aufrufe'], color='#1DA1F2', linewidth=1.5, alpha=0.5, label=f'Tägliche {y_label}')
        
        ax.plot(df.index, df['Trend'], color='#FFD700', linewidth=3, label='7-Tage Trend')

        max_views_str = f"{int(max_views):,}".replace(',', '.')
        
        ax.annotate(f'Peak: {max_views_str}',
                    xy=(max_date, max_views),
                    xytext=(10, 20),
                    textcoords='offset points',
                    color='white',
                    fontweight='bold',
                    arrowprops=dict(arrowstyle="->", color='#FFD700', lw=1.5))

        # NEU: Der Titel passt sich der Datenquelle an (z.B. "NASA Trend: ...")
        plt.title(f'{source_name} Trend: {thema_clean}', color='white', fontsize=16, fontweight='bold', pad=15)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d. %b'))
        plt.xticks(rotation=45, color='#8899a6')
        plt.yticks(color='#8899a6')
        
        for spine in ax.spines.values():
            spine.set_color('#38444d')
            
        ax.legend(facecolor=bg_color, edgecolor='#38444d', labelcolor='white')

        plt.tight_layout()
        plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        print(f"✅ Grafik erfolgreich gespeichert unter: {chart_path}")
        return chart_path
        
    except Exception as e:
        print(f"❌ Fehler bei der Grafikerstellung: {e}")
        return None
