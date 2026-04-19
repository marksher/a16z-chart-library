"""Big number example — default theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
from chart_library import big_number, save_png, save_svg

OUT = os.path.dirname(__file__)

_CFG = os.path.join(os.path.dirname(__file__), "big_number.json")


def make_fig(cfg_path=_CFG):
    """Return the big number figure (used in all.html gallery)."""
    with open(cfg_path) as f:
        cfg = json.load(f)
    return big_number(**cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "big_number.png"))
    save_svg(fig, os.path.join(OUT, "big_number.svg"))
    fig.write_html(os.path.join(OUT, "big_number.html"))
    print("big_number.png + big_number.svg written")
