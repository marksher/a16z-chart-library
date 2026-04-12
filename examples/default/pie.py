"""Pie / donut chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from chart_library import pie, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "category": ["Foundation Models", "Developer Tools", "Enterprise AI",
                  "Consumer AI", "Infrastructure", "Other"],
    "share": [38, 22, 18, 12, 7, 3],
})
fig = pie(df, labels="category", values="share",
          title="AI Investment by Category", source="PitchBook", theme=None)
save_png(fig, os.path.join(OUT, "pie.png"))
fig.write_html(os.path.join(OUT, "pie.html"))
print("pie.png written")
