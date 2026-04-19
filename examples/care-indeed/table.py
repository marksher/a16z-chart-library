"""Table example — care-indeed theme."""

import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from chart_library import table, save_png, save_svg

OUT = os.path.dirname(__file__)
_CFG = os.path.join(os.path.dirname(__file__), "table.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    df = pd.DataFrame(cfg.pop("data"))
    return table(df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "table.png"))
    save_svg(fig, os.path.join(OUT, "table.svg"))
    fig.write_html(os.path.join(OUT, "table.html"))
    print("table.png written")
