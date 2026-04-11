"""Donut chart demo — modeled after a16z enterprise AI penetration"""
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import a16z_charts as a16z

a16z.use_theme()
OUTPUT_FILE = Path(__file__).with_name("pie_demo.png")

data = pd.DataFrame({
    "segment": ["Using AI", "Evaluating", "Not Yet"],
    "pct":     [29, 38, 33],
})

fig, ax = a16z.donut_chart(
    data,
    labels="segment",
    values="pct",
    title="Enterprise AI Adoption — Fortune 500",
    subtitle="Share of companies by adoption stage, 2025",
    source="a16z Research",
)

fig.savefig(OUTPUT_FILE)
print(f"Saved: {OUTPUT_FILE.relative_to(SCRIPTS_DIR.parent).as_posix()}")
