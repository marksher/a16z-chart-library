"""Area chart demo — modeled after a16z global liquids supply build-up"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import a16z_charts as a16z

a16z.use_theme()
OUTPUT_FILE = Path(__file__).with_name("area_demo.png")

data = pd.DataFrame({
    "month":       ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
    "Production":  [92.1, 92.4, 92.8, 93.1, 93.5, 93.9, 94.2],
    "US SPR":      [0.3,  0.3,  0.4,  0.4,  0.3,  0.3,  0.4],
    "Row Stocks":  [1.2,  1.4,  1.1,  1.3,  1.5,  1.2,  1.4],
    "Asian Stocks":[0.8,  0.9,  0.7,  0.8,  0.9,  1.0,  0.8],
})

fig, ax = a16z.area_chart(
    data,
    x="month",
    y=["Production", "US SPR", "Row Stocks", "Asian Stocks"],
    title="YTD Global Landed Liquids Supply",
    subtitle="Million barrels per day",
    source="HTM Energy Partners",
    stacked=True,
)

ax.set_ylabel("Million barrels / day", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig(OUTPUT_FILE)
print(f"Saved: {OUTPUT_FILE.relative_to(SCRIPTS_DIR.parent).as_posix()}")
