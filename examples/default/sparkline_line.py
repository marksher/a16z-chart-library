"""SparklineLine example — default theme."""

import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from chart_library import sparkline_line, save_png, save_svg

OUT = os.path.dirname(__file__)
_CFG = os.path.join(os.path.dirname(__file__), "sparkline_line.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    df = pd.DataFrame(cfg.pop("data"))
    return sparkline_line(df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_line.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_line.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_line.html"))
    print("sparkline_line.png written")
