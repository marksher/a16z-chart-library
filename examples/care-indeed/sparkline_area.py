"""Sparkline area example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import yaml
import sparkline_line as _src
from chart_library import sparkline_area, save_png, save_svg

OUT = os.path.dirname(__file__)


_YAML = os.path.join(os.path.dirname(__file__), "sparkline_area.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return sparkline_area(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_area.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_area.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_area.html"))
    print("sparkline_area.png + sparkline_area.svg written")
