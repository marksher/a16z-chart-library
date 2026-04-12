"""Sparkline bar example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

from chart_library import sparkline_bar, save_png, save_svg
from sparkline_line import _df

OUT = os.path.dirname(__file__)


def make_fig():
    return sparkline_bar(
        _df,
        x="month",
        y=["GPT-4o", "Claude", "Gemini"],
        theme="a16z-news",
        width=300,
        height=80,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_bar.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_bar.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_bar.html"))
    print("sparkline_bar.png + sparkline_bar.svg written")
