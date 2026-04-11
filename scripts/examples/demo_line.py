"""Line chart demo — modeled after a16z electricity consumption projections"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import a16z_charts as a16z

a16z.use_theme()
OUTPUT_FILE = Path(__file__).with_name("line_demo.png")

years = list(range(2015, 2031))
data = pd.DataFrame({
    "year": years,
    "History":  [100,102,101,103,105,104,103,106,102,108,111,114,None,None,None,None],
    "McKinsey": [None]*10 + [111,116,121,128,136,145],
    "NEMA":     [None]*10 + [111,115,119,124,130,136],
    "EIA":      [None]*10 + [111,113,115,117,119,121],
})

fig, ax = a16z.line_chart(
    data,
    x="year",
    y=["History", "McKinsey", "NEMA", "EIA"],
    title="U.S. Electricity Demand Projections",
    subtitle="Index (2025 = 100) — dashed lines are forecasts",
    source="EIA, McKinsey, NEMA",
    dashed=["McKinsey", "NEMA", "EIA"],
)

ax.set_ylabel("Index (2025 = 100)", color=a16z.TEXT_MID, fontfamily="sans-serif")
fig.savefig(OUTPUT_FILE)
print(f"Saved: {OUTPUT_FILE.relative_to(SCRIPTS_DIR.parent).as_posix()}")
