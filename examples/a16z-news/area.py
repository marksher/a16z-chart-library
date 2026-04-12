"""Area chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import yaml
import pandas as pd
from chart_library import area, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "year": [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
    "Permian Basin": [2,  4,  8,  14, 18, 16, 22, 28],
    "Appalachia":    [5,  9,  14, 18, 21, 22, 24, 25],
    "Haynesville":   [3,  6,  8,  7,  9,  11, 14, 16],
    "Eagle Ford":    [1,  3,  7,  8,  7,  6,  7,  8],
    "Other":         [14, 13, 12, 11, 11, 11, 11, 10],
})


_YAML = os.path.join(os.path.dirname(__file__), "area.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return area(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "area.png"))
    save_svg(fig, os.path.join(OUT, "area.svg"))
    fig.write_html(os.path.join(OUT, "area.html"))
    print("area.png + area.svg written")
