"""Scatter chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import scatter as _src
from chart_library import scatter, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    fig = scatter(
        _src._df,
        x="cost",
        y="usage",
        title="Cost vs. Usage Based on Source",
        subtitle="Total monthly token usage (log scale) vs. cost per 1M tokens (log scale)",
        source="OpenRouter",
        color_col="type",
        label_col="model",
        theme="care-indeed",
        width=900,
        height=580,
    )
    fig.update_xaxes(type="log", title_text="Cost per 1M Tokens ($)")
    fig.update_yaxes(type="log", title_text="Total Usage in Millions of Tokens")
    return fig


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "scatter.png"))
    save_svg(fig, os.path.join(OUT, "scatter.svg"))
    fig.write_html(os.path.join(OUT, "scatter.html"))
    print("scatter.png + scatter.svg written")
