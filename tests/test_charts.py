"""Smoke tests for chart_library — verify each chart type returns a Figure."""

import sys
import os
import tempfile
import re

import pytest
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from chart_library import (
    bar, line, area, scatter, pie, table, map_chart,
    diverging_bar, sparkline_line, sparkline_area, sparkline_bar,
    stat_card, big_number, gauge,
    load_theme, Theme,
    save_png, save_svg,
)


# ── Sample data ──────────────────────────────────────────────────────────────

DF_XY = pd.DataFrame({
    "x": ["A", "B", "C", "D"],
    "y": [10, 25, 15, 30],
    "y2": [5, 12, 8, 20],
})

DF_MULTI = pd.DataFrame({
    "year": ["2022", "2023", "2024"],
    "Series A": [10, 20, 30],
    "Series B": [15, 25, 35],
})

DF_PIE = pd.DataFrame({
    "category": ["Alpha", "Beta", "Gamma"],
    "share": [40, 35, 25],
})

DF_MAP = pd.DataFrame({
    "country": ["USA", "CHN", "GBR"],
    "value": [100, 80, 50],
})

DF_DIVERGE = pd.DataFrame({
    "topic": ["Economy", "Healthcare", "Education"],
    "sentiment": [12, -8, 5],
})

DF_SPARK = pd.DataFrame({
    "t": list(range(10)),
    "v": [1, 3, 2, 5, 4, 6, 5, 8, 7, 9],
})


# ── Chart smoke tests ────────────────────────────────────────────────────────

@pytest.mark.parametrize("theme", ["a16z-news", None])
class TestChartTypes:
    def test_bar(self, theme):
        fig = bar(DF_XY, x="x", y="y", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_bar_multi(self, theme):
        fig = bar(DF_MULTI, x="year", y=["Series A", "Series B"], stacked=True, theme=theme)
        assert isinstance(fig, go.Figure)

    def test_line(self, theme):
        fig = line(DF_MULTI, x="year", y=["Series A", "Series B"], theme=theme)
        assert isinstance(fig, go.Figure)

    def test_area(self, theme):
        fig = area(DF_MULTI, x="year", y=["Series A", "Series B"], theme=theme)
        assert isinstance(fig, go.Figure)

    def test_scatter(self, theme):
        fig = scatter(DF_XY, x="x", y="y", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_pie(self, theme):
        fig = pie(DF_PIE, labels="category", values="share", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_table(self, theme):
        fig = table(DF_XY, theme=theme)
        assert isinstance(fig, go.Figure)

    def test_map_chart(self, theme):
        fig = map_chart(DF_MAP, locations="country", values="value", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_diverging_bar(self, theme):
        fig = diverging_bar(DF_DIVERGE, y="topic", x="sentiment", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_sparkline_line(self, theme):
        fig = sparkline_line(DF_SPARK, x="t", y="v", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_sparkline_area(self, theme):
        fig = sparkline_area(DF_SPARK, x="t", y="v", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_sparkline_bar(self, theme):
        fig = sparkline_bar(DF_SPARK, x="t", y="v", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_stat_card(self, theme):
        fig = stat_card(value="1,234", label="Users", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_big_number(self, theme):
        fig = big_number(value="$5.2M", label="Revenue", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_big_number_no_label(self, theme):
        fig = big_number(value=42, theme=theme)
        assert isinstance(fig, go.Figure)

    def test_gauge(self, theme):
        fig = gauge(value=73, label="Score", theme=theme)
        assert isinstance(fig, go.Figure)

    def test_gauge_zero(self, theme):
        fig = gauge(value=0, label="No Show Rate", theme=theme)
        assert isinstance(fig, go.Figure)


# ── Theme tests ──────────────────────────────────────────────────────────────

class TestTheme:
    def test_load_builtin(self):
        t = load_theme("a16z-news")
        assert isinstance(t, Theme)
        assert t.name == "a16z-news"
        assert len(t.palette) > 0

    def test_load_none(self):
        assert load_theme(None) is None

    def test_load_invalid_raises(self):
        with pytest.raises(FileNotFoundError):
            load_theme("nonexistent-theme")

    def test_passthrough(self):
        t = load_theme("a16z-news")
        assert load_theme(t) is t

    def test_stat_card_overrides(self):
        t = load_theme("a16z-news")
        assert isinstance(t.stat_card, dict)

    def test_big_number_overrides(self):
        t = load_theme("a16z-news")
        assert isinstance(t.big_number, dict)


# ── Export tests ─────────────────────────────────────────────────────────────

class TestExport:
    def _simple_fig(self):
        return bar(DF_XY, x="x", y="y", theme="a16z-news")

    def test_save_png(self):
        fig = self._simple_fig()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            save_png(fig, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_save_svg(self):
        fig = self._simple_fig()
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            save_svg(fig, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


# ── Visual regression tests ──────────────────────────────────────────────────
# Verify PNG/SVG outputs have correct dimensions, contain expected text,
# and are not blank/empty.

THEMED_CHARTS = [
    ("bar",            lambda t: bar(DF_MULTI, x="year", y=["Series A", "Series B"],
                            title="Test Title", subtitle="Test Subtitle", stacked=True, theme=t)),
    ("line",           lambda t: line(DF_MULTI, x="year", y=["Series A", "Series B"],
                            title="Line Title", subtitle="Line Sub", theme=t)),
    ("area",           lambda t: area(DF_MULTI, x="year", y=["Series A", "Series B"],
                            title="Area Title", theme=t)),
    ("pie",            lambda t: pie(DF_PIE, labels="category", values="share",
                            title="Pie Title", theme=t)),
    ("diverging_bar",  lambda t: diverging_bar(DF_DIVERGE, y="topic", x="sentiment",
                            title="Diverging Title", theme=t)),
    ("stat_card",      lambda t: stat_card(value="1,234", label="Users", theme=t)),
    ("big_number",     lambda t: big_number(value="$5.2M", label="Revenue", theme=t)),
    ("gauge",          lambda t: gauge(value=73, label="Score", theme=t)),
]


@pytest.mark.parametrize("theme", ["a16z-news", "care-indeed", None])
class TestVisualOutput:
    """Verify PNG exports are non-blank and SVG exports contain expected content."""

    @pytest.mark.parametrize("name,make_fig_fn", THEMED_CHARTS, ids=[c[0] for c in THEMED_CHARTS])
    def test_png_not_blank(self, theme, name, make_fig_fn):
        fig = make_fig_fn(theme)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            save_png(fig, path)
            img = Image.open(path)
            # Check dimensions are reasonable
            assert img.width >= 200
            assert img.height >= 100
            # Check image is not all one color (blank)
            colors = img.getcolors(maxcolors=10)
            assert colors is None or len(colors) > 1, f"{name} PNG appears blank (single color)"
        finally:
            os.unlink(path)

    @pytest.mark.parametrize("name,make_fig_fn", THEMED_CHARTS, ids=[c[0] for c in THEMED_CHARTS])
    def test_svg_has_content(self, theme, name, make_fig_fn):
        fig = make_fig_fn(theme)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as f:
            path = f.name
        try:
            save_svg(fig, path)
            with open(path) as f:
                svg = f.read()
            assert "<svg" in svg, f"{name} SVG missing <svg> tag"
            assert len(svg) > 500, f"{name} SVG suspiciously small ({len(svg)} bytes)"
            # Charts with titles should have the title text in SVG
            if name in ("bar", "line", "area", "pie", "diverging_bar"):
                assert "Title" in svg, f"{name} SVG missing title text"
        finally:
            os.unlink(path)


class TestTitleRendering:
    """Verify titles appear in output for both themed and unthemed charts."""

    def test_themed_title_in_svg(self):
        fig = bar(DF_XY, x="x", y="y", title="MyTestTitle", theme="a16z-news")
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as f:
            path = f.name
        try:
            save_svg(fig, path)
            with open(path) as f:
                svg = f.read()
            assert "MyTestTitle" in svg
        finally:
            os.unlink(path)

    def test_unthemed_title_in_svg(self):
        fig = bar(DF_XY, x="x", y="y", title="PlainTitle", theme=None)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as f:
            path = f.name
        try:
            save_svg(fig, path)
            with open(path) as f:
                svg = f.read()
            assert "PlainTitle" in svg
        finally:
            os.unlink(path)

    def test_themed_subtitle_in_svg(self):
        fig = line(DF_MULTI, x="year", y=["Series A"], title="T", subtitle="MySub", theme="a16z-news")
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as f:
            path = f.name
        try:
            save_svg(fig, path)
            with open(path) as f:
                svg = f.read()
            assert "MySub" in svg
        finally:
            os.unlink(path)

    def test_unthemed_subtitle_in_svg(self):
        fig = line(DF_MULTI, x="year", y=["Series A"], title="T", subtitle="PlainSub", theme=None)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as f:
            path = f.name
        try:
            save_svg(fig, path)
            with open(path) as f:
                svg = f.read()
            assert "PlainSub" in svg
        finally:
            os.unlink(path)
