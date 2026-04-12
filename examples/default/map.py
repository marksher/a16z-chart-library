"""Map chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from a16z_charts import map_chart, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "country": ["USA", "CHN", "GBR", "IND", "DEU", "ISR", "FRA", "CAN", "SGP", "AUS"],
    "investment_b": [120, 55, 18, 15, 12, 10, 9, 8, 7, 6],
})
fig = map_chart(df, locations="country", values="investment_b",
                title="Global AI Investment", source="PitchBook", theme=None)
save_png(fig, os.path.join(OUT, "map.png"))
fig.write_html(os.path.join(OUT, "map.html"))
print("map.png written")
