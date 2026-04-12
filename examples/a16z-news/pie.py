"""
Pie / donut chart example — a16z-news theme.

Demonstrates a donut chart showing AI investment by category,
matching the visual style of a16z.news.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from a16z_charts import pie, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "category": [
        "Foundation Models",
        "Developer Tooling",
        "Enterprise AI",
        "Consumer AI",
        "AI Infrastructure",
        "Other",
    ],
    "share": [38, 22, 18, 12, 7, 3],
})

fig = pie(
    df,
    labels="category",
    values="share",
    title="AI Investment by Category",
    subtitle="Percentage of total venture investment, 2025",
    source="PitchBook; a16z analysis",
    hole=0.55,
    theme="a16z-news",
    width=700,
    height=520,
)

save_png(fig, os.path.join(OUT, "pie.png"))
fig.write_html(os.path.join(OUT, "pie.html"))
print("pie.png written")
