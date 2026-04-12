"""Bar chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from a16z_charts import bar, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "company": ["Microsoft", "Meta", "Alphabet", "Amazon", "Oracle"],
    "capex_b": [130, 55, 105, 175, 28],
})
fig = bar(df, x="company", y="capex_b",
          title="Hyperscaler Capex 2024", subtitle="Billions USD",
          source="Bloomberg", theme=None, width=800, height=480)
save_png(fig, os.path.join(OUT, "bar.png"))
fig.write_html(os.path.join(OUT, "bar.html"))
print("bar.png written")
