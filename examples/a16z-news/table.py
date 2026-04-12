"""Table chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import yaml
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


_YAML = os.path.join(os.path.dirname(__file__), "table.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return table(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "table.png"))
    save_svg(fig, os.path.join(OUT, "table.svg"))
    fig.write_html(os.path.join(OUT, "table.html"))
    print("table.png + table.svg written")
