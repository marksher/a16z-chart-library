"""Stat card example — default theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
from chart_library import stat_card, save_png, save_svg

OUT = os.path.dirname(__file__)

_CFG = os.path.join(os.path.dirname(__file__), "stat_card.json")


def make_fig(cfg_path=_CFG):
    """Return the stat card figure (used in all.html gallery)."""
    with open(cfg_path) as f:
        cfg = json.load(f)
    return stat_card(**cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "stat_card.png"))
    save_svg(fig, os.path.join(OUT, "stat_card.svg"))
    fig.write_html(os.path.join(OUT, "stat_card.html"))
    print("stat_card.png + stat_card.svg written")
