"""
Area chart example — a16z-news theme.

Demonstrates a stacked area chart showing natural gas production by play,
matching the style of a16z.news energy charts.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from a16z_charts import area, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "year": [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
    "Permian Basin": [2,  4,  8,  14, 18, 16, 22, 28],
    "Appalachia":    [5,  9,  14, 18, 21, 22, 24, 25],
    "Haynesville":   [3,  6,  8,  7,  9,  11, 14, 16],
    "Eagle Ford":    [1,  3,  7,  8,  7,  6,  7,  8],
    "Other":         [14, 13, 12, 11, 11, 11, 11, 10],
})

fig = area(
    df,
    x="year",
    y=["Permian Basin", "Appalachia", "Haynesville", "Eagle Ford", "Other"],
    title="US Marketable Natural Gas Production by Play",
    subtitle="Bcf/d",
    source="EIA; Natural Gas Intelligence; Wood Mackenzie",
    stacked=True,
    theme="a16z-news",
    width=900,
    height=560,
)

save_png(fig, os.path.join(OUT, "area.png"))
fig.write_html(os.path.join(OUT, "area.html"))
print("area.png written")
