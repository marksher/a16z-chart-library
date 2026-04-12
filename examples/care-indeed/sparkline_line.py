"""Sparkline line example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import sparkline_line as _src
from chart_library import sparkline_line, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return sparkline_line(
        _src._df,
        x="month",
        y=["GPT-4o", "Claude", "Gemini"],
        end_dot=True,
        theme="care-indeed",
        width=300,
        height=80,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_line.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_line.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_line.html"))
    print("sparkline_line.png + sparkline_line.svg written")
