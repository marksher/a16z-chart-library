"""Pie / donut chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import yaml
import pandas as pd
from chart_library import pie, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "category": [
        "Foundation Models",
        "Developer Tooling",
        "Enterprise AI",
        "Consumer AI",
        "AI Infrastructure",
        "Other",
    ],
    "share": [38, 22, 18, 12, 7, 3],
})


_YAML = os.path.join(os.path.dirname(__file__), "pie.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return pie(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "pie.png"))
    save_svg(fig, os.path.join(OUT, "pie.svg"))
    fig.write_html(os.path.join(OUT, "pie.html"))
    print("pie.png + pie.svg written")
