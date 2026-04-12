"""
Table chart example — a16z-news theme.

Demonstrates a styled data table showing SaaS AI feature pricing strategies,
matching the visual style of a16z.news pricing research charts.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from a16z_charts import table, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "Company": [
        "Salesforce", "HubSpot", "Zendesk", "Intercom",
        "Notion", "GitHub", "Slack", "Zoom",
    ],
    "AI Packaging": [
        "Add-on > core", "Core", "Add-on", "Core",
        "Add-on > core", "Core", "Core", "Add-on",
    ],
    "Billing Model": [
        "Subscription > hybrid", "Hybrid", "Usage", "Hybrid",
        "Subscription", "Subscription", "Subscription", "Subscription",
    ],
    "Status": [
        "Updated", "Stable", "Updated", "Stable",
        "Updated", "Stable", "Stable", "Stable",
    ],
})

fig = table(
    df,
    title="SaaS AI Feature Pricing & Packaging Shifts",
    subtitle="March 2024 – November 2025",
    source="Public pricing pages",
    highlight_rows=[0, 2, 4],   # rows that changed
    theme="a16z-news",
    width=860,
)

save_png(fig, os.path.join(OUT, "table.png"))
fig.write_html(os.path.join(OUT, "table.html"))
print("table.png written")
