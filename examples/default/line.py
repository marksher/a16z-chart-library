"""Line chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from chart_library import line, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "date": ["2022Q1","2022Q3","2023Q1","2023Q3","2024Q1","2024Q3","2025Q1"],
    "Proprietary": [10, 15, 25, 40, 55, 72, 88],
    "Open Weight":  [4,  8,  14, 28, 45, 65, 82],
})
fig = line(df, x="date", y=["Proprietary", "Open Weight"],
           title="Model Benchmark Progress", source="Artificial Analysis",
           end_labels=False, theme=None)
save_png(fig, os.path.join(OUT, "line.png"))
fig.write_html(os.path.join(OUT, "line.html"))
print("line.png written")
