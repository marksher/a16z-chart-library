"""Line chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import line as _src
from chart_library import line, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return line(
        _src._df,
        x="date",
        y=["Proprietary", "Open Weight"],
        title="Open Weight Models Are (Very) Close",
        subtitle="SOTA Proprietary models score higher, but Open Weight models keep narrowing the gap",
        source="Artificial Analysis",
        end_labels=True,
        theme="care-indeed",
        width=900,
        height=560,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "line.png"))
    save_svg(fig, os.path.join(OUT, "line.svg"))
    fig.write_html(os.path.join(OUT, "line.html"))
    print("line.png + line.svg written")
