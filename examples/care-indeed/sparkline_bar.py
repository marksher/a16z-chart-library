"""Sparkline bar example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import yaml
import sparkline_line as _src
from chart_library import sparkline_bar, save_png, save_svg

OUT = os.path.dirname(__file__)


_YAML = os.path.join(os.path.dirname(__file__), "sparkline_bar.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return sparkline_bar(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_bar.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_bar.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_bar.html"))
    print("sparkline_bar.png + sparkline_bar.svg written")
