"""Sparkline line example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import yaml
import sparkline_line as _src
from chart_library import sparkline_line, save_png, save_svg

OUT = os.path.dirname(__file__)


_YAML = os.path.join(os.path.dirname(__file__), "sparkline_line.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return sparkline_line(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_line.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_line.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_line.html"))
    print("sparkline_line.png + sparkline_line.svg written")
