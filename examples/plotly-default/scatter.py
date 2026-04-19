"""Scatter chart example — plotly-default theme (Plotly defaults)."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))

import json
import scatter as _src
from chart_library import scatter, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "scatter.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    fig = scatter(_src._df, **cfg)
    fig.update_xaxes(type="log", title_text="Cost per 1M Tokens ($)")
    fig.update_yaxes(type="log", title_text="Total Usage in Millions of Tokens")
    return fig


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "scatter.png"))
    save_svg(fig, os.path.join(OUT, "scatter.svg"))
    fig.write_html(os.path.join(OUT, "scatter.html"))
    print("scatter.png + scatter.svg written")
