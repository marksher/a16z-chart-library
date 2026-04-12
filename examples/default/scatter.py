"""Scatter chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd, numpy as np
from chart_library import scatter, save_png

OUT = os.path.dirname(__file__)
rng = np.random.default_rng(7)
df = pd.DataFrame({
    "cost":  rng.uniform(0.01, 50, 30),
    "perf":  rng.uniform(10, 95, 30),
    "type":  (["Open"] * 15) + (["Closed"] * 15),
})
fig = scatter(df, x="cost", y="perf",
              title="Model Cost vs. Performance",
              color_col="type", source="Benchmark data", theme=None)
save_png(fig, os.path.join(OUT, "scatter.png"))
fig.write_html(os.path.join(OUT, "scatter.html"))
print("scatter.png written")
