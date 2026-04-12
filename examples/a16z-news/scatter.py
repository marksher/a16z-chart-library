"""Scatter chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
import numpy as np
from chart_library import scatter, save_png, save_svg

OUT = os.path.dirname(__file__)

rng = np.random.default_rng(42)

_open_models = [
    "Llama 3.1 70B", "Mistral 7B", "Gemma 2 9B", "Phi-3 Mini",
    "Qwen 2.5 72B", "DeepSeek V2", "Falcon 180B", "Yi 34B",
]
_closed_models = [
    "GPT-4o", "Claude Sonnet 4", "Gemini 1.5 Pro", "GPT-4 Turbo",
    "Claude Opus 4", "Gemini Ultra", "GPT-4o Mini",
]

_df = pd.concat([
    pd.DataFrame({
        "model": _open_models,
        "cost": rng.uniform(0.0001, 0.5, len(_open_models)),
        "usage": rng.uniform(1, 6, len(_open_models)),
        "type": "Open Source",
    }),
    pd.DataFrame({
        "model": _closed_models,
        "cost": rng.uniform(1, 30, len(_closed_models)),
        "usage": rng.uniform(2, 7, len(_closed_models)),
        "type": "Closed Source",
    }),
], ignore_index=True)


def make_fig():
    fig = scatter(
        _df,
        x="cost",
        y="usage",
        title="Cost vs. Usage Based on Source",
        subtitle="Total monthly token usage (log scale) vs. cost per 1M tokens (log scale)",
        source="OpenRouter",
        color_col="type",
        label_col="model",
        theme="a16z-news",
        width=900,
        height=580,
    )
    # Log scales
    fig.update_xaxes(type="log", title_text="Cost per 1M Tokens ($)")
    fig.update_yaxes(type="log", title_text="Total Usage in Millions of Tokens")
    return fig


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "scatter.png"))
    save_svg(fig, os.path.join(OUT, "scatter.svg"))
    fig.write_html(os.path.join(OUT, "scatter.html"))
    print("scatter.png + scatter.svg written")
