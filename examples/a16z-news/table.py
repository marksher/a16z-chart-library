"""Table chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from chart_library import table, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
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


def make_fig():
    return table(
        _df,
        title="SaaS AI Feature Pricing & Packaging Shifts",
        subtitle="March 2024 – November 2025",
        source="Public pricing pages",
        highlight_rows=[0, 2, 4],
        theme="a16z-news",
        width=860,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "table.png"))
    save_svg(fig, os.path.join(OUT, "table.svg"))
    fig.write_html(os.path.join(OUT, "table.html"))
    print("table.png + table.svg written")
