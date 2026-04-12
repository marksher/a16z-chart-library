"""
Bar chart example — a16z-news theme.

Demonstrates both a single-series horizontal bar and a stacked vertical bar
using the a16z-news visual style.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from a16z_charts import bar, save_png

OUT = os.path.dirname(__file__)

# ── Example 1: Single-series horizontal bar ───────────────────────────────────
df1 = pd.DataFrame({
    "company": [
        "Capital expenditures\non compute",
        "Power",
    ],
    "capex_b": [30.0, 3.0],
})

fig1 = bar(
    df1,
    x="company",
    y="capex_b",
    title="The costs of computational equipment are\naround ten times higher than the costs of\npower in frontier AI data centers",
    subtitle="Cost per GW of power (Billions USD)",
    source="EpochAI",
    orientation="h",
    show_values=False,
    theme="a16z-news",
    width=700,
    height=420,
)

save_png(fig1, os.path.join(OUT, "bar_single.png"))
fig1.write_html(os.path.join(OUT, "bar_single.html"))
print("bar_single.png written")

# ── Example 2: Stacked vertical bar ───────────────────────────────────────────
df2 = pd.DataFrame({
    "year": ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025E", "2026E"],
    "Microsoft": [25, 30, 35, 45, 60, 90, 130, 180, 240],
    "Meta":      [10, 12, 15, 20, 28, 40, 55,  80,  110],
    "Alphabet":  [20, 24, 28, 38, 52, 75, 105, 145, 190],
    "Amazon":    [30, 38, 48, 65, 88, 125, 175, 235, 320],
    "Oracle":    [2,  3,  4,  6,  10, 18,  28,  45,  65],
})

fig2 = bar(
    df2,
    x="year",
    y=["Microsoft", "Meta", "Alphabet", "Amazon", "Oracle"],
    title="Hyperscaler Capex To The Moon",
    subtitle="Combined capital expenditures expected to top $650 billion in 2026",
    source="Bloomberg; 2026 estimates based on the midpoint of guidance for Meta, Alphabet and Amazon, and analyst consensus for Microsoft and Oracle",
    orientation="v",
    stacked=True,
    show_values=False,
    theme="a16z-news",
    width=900,
    height=560,
)

save_png(fig2, os.path.join(OUT, "bar_stacked.png"))
fig2.write_html(os.path.join(OUT, "bar_stacked.html"))
print("bar_stacked.png written")
