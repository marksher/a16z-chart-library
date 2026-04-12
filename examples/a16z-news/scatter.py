"""
Scatter chart example — a16z-news theme.

Demonstrates a categorically-colored scatter chart (Cost vs. Usage by source type),
matching the style of a16z.news AI model charts.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
import numpy as np
from a16z_charts import scatter, save_png

OUT = os.path.dirname(__file__)

rng = np.random.default_rng(42)

open_source_models = [
    "Llama 3.1 70B", "Mistral 7B", "Gemma 2 9B", "Phi-3 Mini",
    "Qwen 2.5 72B", "DeepSeek V2", "Falcon 180B", "Yi 34B",
]
closed_source_models = [
    "GPT-4o", "Claude Sonnet 4", "Gemini 1.5 Pro", "GPT-4 Turbo",
    "Claude Opus 4", "Gemini Ultra", "GPT-4o Mini",
]

open_df = pd.DataFrame({
    "model": open_source_models,
    "cost": rng.uniform(0.0001, 0.5, len(open_source_models)),
    "usage": rng.uniform(1, 6, len(open_source_models)),
    "type": "Open Source",
})
closed_df = pd.DataFrame({
    "model": closed_source_models,
    "cost": rng.uniform(1, 30, len(closed_source_models)),
    "usage": rng.uniform(2, 7, len(closed_source_models)),
    "type": "Closed Source",
})
df = pd.concat([open_df, closed_df], ignore_index=True)

fig = scatter(
    df,
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

# Log scales to match the a16z reference chart
fig.update_xaxes(type="log", title_text="Cost per 1M Tokens ($)")
fig.update_yaxes(type="log", title_text="Total Usage in Millions of Tokens")

save_png(fig, os.path.join(OUT, "scatter.png"))
fig.write_html(os.path.join(OUT, "scatter.html"))
print("scatter.png written")
