"""
Theme dataclass and loader for chart_library.

Usage
-----
from chart_library.themes import load_theme, Theme

t = load_theme("a16z-news")          # built-in theme
t = load_theme("path/to/theme.yaml") # custom theme
t = load_theme(None)                 # Plotly defaults (returns None)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

# Directory containing bundled .yaml theme files
BUNDLED_THEMES_DIR = Path(__file__).parent


@dataclass
class Theme:
    name: str
    background: str
    plot_background: str
    text: dict
    palette: list
    fonts: dict
    font_sizes: dict
    font_weights: dict
    margins: dict
    grid: dict
    spines: dict
    legend: dict
    branding: dict
    source: dict
    # Per-chart-type overrides (optional, default to empty dict)
    bar: dict = field(default_factory=dict)
    line: dict = field(default_factory=dict)
    area: dict = field(default_factory=dict)
    scatter: dict = field(default_factory=dict)
    pie: dict = field(default_factory=dict)
    table: dict = field(default_factory=dict)
    map: dict = field(default_factory=dict)
    stat_card: dict = field(default_factory=dict)
    big_number: dict = field(default_factory=dict)
    # Extra YAML keys are silently ignored via __post_init__
    version: str = "1.0"
    description: str = ""

    def __post_init__(self):
        pass


def load_theme(theme) -> Optional[Theme]:
    """
    Resolve *theme* to a Theme instance, or None for Plotly defaults.

    Parameters
    ----------
    theme : None | str | dict | Theme
        - None           → returns None (caller uses Plotly defaults)
        - "a16z-news"    → loads the bundled a16z-news.yaml
        - "/path/to.yaml"→ loads from an absolute or relative path
        - dict           → constructs a Theme from a plain dict
        - Theme          → returned as-is
    """
    if theme is None:
        return None

    if isinstance(theme, Theme):
        return theme

    if isinstance(theme, dict):
        # Allow extra keys in the dict without crashing
        valid_fields = {f.name for f in Theme.__dataclass_fields__.values()}
        filtered = {k: v for k, v in theme.items() if k in valid_fields}
        return Theme(**filtered)

    # String: either a bare name ("a16z-news") or a file path
    path = Path(str(theme))

    if not path.suffix:
        # Bare name — look for a bundled theme
        candidate = BUNDLED_THEMES_DIR / f"{theme}.yaml"
        if not candidate.exists():
            available = [p.stem for p in BUNDLED_THEMES_DIR.glob("*.yaml")]
            raise FileNotFoundError(
                f"Theme '{theme}' not found. "
                f"Available built-in themes: {available}. "
                f"Pass a file path for custom themes."
            )
        path = candidate

    if not path.exists():
        raise FileNotFoundError(f"Theme file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Accept only known fields to avoid dataclass errors on forward-compat keys
    valid_fields = {f.name for f in Theme.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in valid_fields}

    # Resolve branding.image relative to the YAML file so themes are portable
    branding = filtered.get("branding")
    if isinstance(branding, dict):
        img = branding.get("image")
        if img and not img.startswith(("http://", "https://", "data:")):
            img_path = Path(img)
            if not img_path.is_absolute():
                resolved = (path.parent / img_path).resolve()
                if resolved.exists():
                    branding["image"] = str(resolved)

    return Theme(**filtered)
