"""
Geographic choropleth map.

Design note: uses the same universal title / subtitle / source / branding
treatment as all other chart types.  Land and ocean colors come from the
theme so the map feels like it belongs in the same document as the bar
and line charts.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def map_chart(
    data,
    locations: str,
    values: str,
    location_mode: str = "ISO-3",
    title: str = "",
    subtitle: str = None,
    source: str = None,
    theme="a16z-news",
    width: int = 900,
    height: int = 500,
) -> go.Figure:
    """
    Choropleth geographic map.

    Parameters
    ----------
    data          : pd.DataFrame or list-of-dicts
    locations     : column with ISO-3 country codes or US state abbreviations
    values        : column with numeric values to color-encode
    location_mode : 'ISO-3' (world countries) | 'USA-states'
    theme         : 'a16z-news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> import pandas as pd
    >>> from a16z_charts import map_chart
    >>> df = pd.DataFrame({"country": ["USA","GBR","DEU"], "value": [100, 60, 45]})
    >>> fig = map_chart(df, locations="country", values="value", title="Investment")
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty — pass a DataFrame with at least one row")

    for col in [locations, values]:
        if col not in df.columns:
            raise ValueError(f"column '{col}' not found. Available: {list(df.columns)}")

    t = load_theme(theme)
    palette = t.palette if t else None

    land_color = t.map.get("land_color", "#E8E4DC") if t else "#E8E4DC"
    ocean_color = t.map.get("ocean_color", "#D4D0CA") if t else "#D4D0CA"
    border_color = t.map.get("border_color", "#C8C0B4") if t else "#C8C0B4"
    bg = t.background if t else "white"

    # Build a two-stop colorscale from a light neutral to the primary palette color
    if palette and len(palette) >= 1:
        colorscale = [
            [0.0, land_color],         # zero value = land color
            [1.0, palette[0]],         # max value = primary (maroon)
        ]
    else:
        colorscale = "Reds"

    colorbar_font = dict(
        family=t.fonts["family"] if t else "serif",
        color=t.text.get("axis", "#9AA3AC") if t else "#9AA3AC",
        size=t.font_sizes.get("axis_tick", 10) if t else 10,
    )

    plotly_location_mode = "ISO-3" if location_mode == "ISO-3" else "USA-states"

    fig = go.Figure(go.Choropleth(
        locations=df[locations],
        z=df[values],
        locationmode=plotly_location_mode,
        colorscale=colorscale,
        marker_line_color=border_color,
        marker_line_width=0.5,
        colorbar=dict(
            title=dict(
                text=values,
                font=colorbar_font,
            ),
            tickfont=colorbar_font,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    ))

    geo_kwargs = dict(
        bgcolor=bg,
        landcolor=land_color,
        oceancolor=ocean_color,
        showocean=True,
        showland=True,
        showframe=False,
        showcoastlines=True,
        coastlinecolor=border_color,
        coastlinewidth=0.5,
        showcountries=True,
        countrycolor=border_color,
        countrywidth=0.5,
    )

    if location_mode == "USA-states":
        geo_kwargs["scope"] = "usa"
        geo_kwargs["projection_type"] = "albers usa"
        # Remove ocean for US maps (cleaner look)
        geo_kwargs["showocean"] = False
        geo_kwargs["bgcolor"] = bg
    else:
        geo_kwargs["projection_type"] = "natural earth"

    fig.update_geos(**geo_kwargs)

    # Maps have no traditional legend; hide it
    fig.update_layout(showlegend=False)

    return _apply_theme(fig, t, title, subtitle, source, width, height)
