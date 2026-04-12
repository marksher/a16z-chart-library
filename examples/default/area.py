"""Area chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from a16z_charts import area, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "year": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "Hyperscaler": [100, 130, 175, 240, 310, 420, 570],
    "Enterprise":  [200, 210, 220, 230, 240, 250, 260],
    "Colocation":  [150, 155, 162, 168, 174, 180, 186],
})
fig = area(df, x="year", y=["Hyperscaler", "Enterprise", "Colocation"],
           title="Data Center Capacity Growth", source="Synergy Research", theme=None)
save_png(fig, os.path.join(OUT, "area.png"))
fig.write_html(os.path.join(OUT, "area.html"))
print("area.png written")
