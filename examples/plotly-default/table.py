"""Table chart example — plotly-default theme (Plotly defaults)."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))

import json
import table as _src
from chart_library import table, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "table.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return table(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "table.png"))
    save_svg(fig, os.path.join(OUT, "table.svg"))
    fig.write_html(os.path.join(OUT, "table.html"))
    print("table.png + table.svg written")
