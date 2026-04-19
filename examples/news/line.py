"""Line chart example — default theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
import pandas as pd
from chart_library import line, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "date": [
        "Nov'22", "Mar'23", "Jul'23", "Nov'23",
        "Mar'24", "Jul'24", "Nov'24", "Mar'25",
    ],
    "Proprietary": [10, 15, 22, 32, 42, 52, 65, 80],
    "Open Weight":  [4,  8,  14, 22, 34, 46, 60, 76],
})


_CFG = os.path.join(os.path.dirname(__file__), "line.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return line(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "line.png"))
    save_svg(fig, os.path.join(OUT, "line.svg"))
    fig.write_html(os.path.join(OUT, "line.html"))
    print("line.png + line.svg written")
