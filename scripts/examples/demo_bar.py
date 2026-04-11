"""Bar chart demo — modeled after a16z 'Where the Money's Flowing in Enterprise AI'"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import a16z_charts as a16z

a16z.use_theme()
OUTPUT_FILE = Path(__file__).with_name("bar_demo.png")

data = pd.DataFrame({
    "category": [
        "Coding & Dev Tools", "Data & Analytics", "Customer Support",
        "Sales & Marketing", "Healthcare", "Legal & Compliance",
        "Finance & Accounting", "HR & Recruiting",
    ],
    "investment_b": [4.2, 3.1, 2.8, 2.3, 1.9, 1.4, 1.1, 0.8],
})

fig, ax = a16z.bar_chart(
    data,
    x="category",
    y="investment_b",
    title="Where the Money's Flowing in Enterprise AI",
    subtitle="Venture investment by category, 2024 ($B)",
    source="PitchBook, a16z Research",
    orientation="h",
)

ax.set_xlabel("Investment ($B)", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig(OUTPUT_FILE)
print(f"Saved: {OUTPUT_FILE.relative_to(SCRIPTS_DIR.parent).as_posix()}")
