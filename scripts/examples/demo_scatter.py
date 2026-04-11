"""Scatter + dumbbell demo — modeled after a16z streaming prices chart"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import a16z_charts as a16z

a16z.use_theme()
OUTPUT_FILE = Path(__file__).with_name("scatter_dumbbell_demo.png")

# Dumbbell: streaming service price ranges (ads vs ad-free)
data = pd.DataFrame({
    "service":   ["Hulu", "Disney+", "HBO Max", "Netflix", "Peacock", "Paramount+"],
    "with_ads":  [7.99,   7.99,      9.99,      7.99,      5.99,      5.99],
    "ad_free":   [17.99,  13.99,     15.99,     22.99,     13.99,     11.99],
})

fig, ax = a16z.scatter_chart(
    data,
    x=None, y=None,
    title="Streaming Prices Keep Climbing",
    subtitle="Monthly price with ads vs. ad-free, 2025",
    source="Company websites",
    dumbbell=True,
    dumbbell_y="service",
    dumbbell_start="with_ads",
    dumbbell_end="ad_free",
)

ax.set_xlabel("Monthly Price ($)", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig(OUTPUT_FILE)
print(f"Saved: {OUTPUT_FILE.relative_to(SCRIPTS_DIR.parent).as_posix()}")
