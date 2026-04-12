"""
Map chart example — a16z-news theme.

Demonstrates a world choropleth map showing AI investment by country,
using the a16z-news visual style with warm land and ocean colors.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from a16z_charts import map_chart, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "country": [
        "USA", "CHN", "GBR", "IND", "DEU",
        "ISR", "FRA", "CAN", "SGP", "AUS",
        "JPN", "KOR", "SWE", "NLD", "BRA",
    ],
    "investment_b": [
        120, 55, 18, 15, 12,
        10,  9,  8,  7,  6,
        5,   4,  4,  3,  3,
    ],
})

fig = map_chart(
    df,
    locations="country",
    values="investment_b",
    location_mode="ISO-3",
    title="Global AI Investment",
    subtitle="Venture capital investment in AI companies, 2025 (Billions USD)",
    source="PitchBook; a16z analysis",
    theme="a16z-news",
    width=900,
    height=500,
)

save_png(fig, os.path.join(OUT, "map.png"))
fig.write_html(os.path.join(OUT, "map.html"))
print("map.png written")
