"""Sparkline line example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import yaml
import pandas as pd
from chart_library import sparkline_line, save_png, save_svg

OUT = os.path.dirname(__file__)

# Monthly AI model usage index (Jan–Dec 2025)
_df = pd.DataFrame({
    "month": list(range(1, 13)),
    "GPT-4o":    [100, 108, 119, 132, 148, 163, 175, 184, 196, 210, 228, 245],
    "Claude":    [42,  51,  63,  78,  95,  115, 138, 162, 183, 201, 220, 242],
    "Gemini":    [38,  44,  50,  59,  70,  82,  95,  108, 119, 128, 138, 150],
})


_YAML = os.path.join(os.path.dirname(__file__), "sparkline_line.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return sparkline_line(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_line.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_line.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_line.html"))
    print("sparkline_line.png + sparkline_line.svg written")
