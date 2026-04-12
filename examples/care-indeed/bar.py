"""Bar chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import yaml
import bar as _src
from chart_library import bar, save_png, save_svg

OUT = os.path.dirname(__file__)


_YAML = os.path.join(os.path.dirname(__file__), "bar.yaml")


def make_fig(yaml_path=_YAML):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    return bar(_src._df2, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "bar_stacked.png"))
    save_svg(fig, os.path.join(OUT, "bar_stacked.svg"))
    fig.write_html(os.path.join(OUT, "bar_stacked.html"))
    print("bar_stacked.png + bar_stacked.svg written")
