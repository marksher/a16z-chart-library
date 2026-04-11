"""
Color palette for the a16z.news chart style.
"""

# ── Structural colors ─────────────────────────────────────────────────────────
BACKGROUND  = "#F5F0E8"   # warm off-white parchment
TEXT_DARK   = "#1C2B3A"   # near-black — titles
TEXT_MID    = "#5A6472"   # mid-gray — axis labels, subtitles
TEXT_LIGHT  = "#9AA3AC"   # light gray — tick labels, gridlines

GRID_COLOR  = "#E0DAD0"   # very light warm grid lines
SPINE_COLOR = "#C8C0B4"   # axis border color

# ── Data colors (ordered by frequency of use in a16z charts) ─────────────────
TEAL        = "#2B6C8F"   # primary — bars, first series
MAROON      = "#8B3A3A"   # secondary — second series, contrast lines
GOLD        = "#C4A575"   # accent — area fills, annotation highlights
NAVY        = "#1F3B54"   # dark emphasis — table headers, overlays
GREEN       = "#4A7C59"   # third categorical color
LIGHT_BLUE  = "#A8D5E8"   # light fill — stacked area backgrounds
SALMON      = "#D89B9E"   # fourth categorical

# ── Ordered palette list (use in sequence for multi-series charts) ────────────
PALETTE = [TEAL, MAROON, GOLD, GREEN, LIGHT_BLUE, SALMON, NAVY]

# ── Semantic palettes ─────────────────────────────────────────────────────────
PALETTE_DIVERGING   = [MAROON, GOLD, TEAL]      # negative → neutral → positive
PALETTE_SEQUENTIAL  = ["#D0E8F5", "#A8D5E8", "#6BAEC6", TEAL, NAVY]
PALETTE_CATEGORICAL = PALETTE
