"""Theming system for mdview diagram renderers.

Provides a Theme dataclass with all color slots used across renderers,
built-in themes (tokyonight dark/light), and YAML theme loading from
~/.config/mdview/themes/.

Usage:
    from mdview.themes import Theme, BUILTIN_THEMES, load_theme

    # Use built-in theme
    theme = BUILTIN_THEMES["tokyonight"]

    # Load custom theme from file
    theme = load_theme("mytheme")  # ~/.config/mdview/themes/mytheme.yaml

    # Generate CSS for SVG rendering
    css = theme.svg_css()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for one scheme (dark or light)."""

    # Backgrounds
    bg: str                  # Main diagram background
    bg_secondary: str        # Code/fill backgrounds (actor boxes, header bg)

    # Text
    fg: str                  # Body text
    heading: str             # Headings, borders
    header_text: str         # Section headers, actor text
    label: str               # Arrow/message labels

    # Structure
    border: str              # Box borders, table borders
    separator: str           # Section separators
    muted: str               # Subtle elements (lifelines)

    # Connections
    arrow: str               # Arrow lines and heads
    arrow_label_bg: str      # Arrow label background (usually same as bg)


@dataclass(frozen=True)
class Theme:
    """Complete theme with dark and light color schemes."""

    name: str
    dark: ThemeColors
    light: ThemeColors
    font_family: str = "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace"
    font_size: str = "13px"

    def svg_css(self) -> str:
        """Generate the shared THEME_CSS <style> block for SVG diagrams."""
        d = self.dark
        l = self.light
        return f"""
  <style>
    .mdview-diagram {{ font-family: {self.font_family}; font-size: {self.font_size}; }}
    .mdview-diagram .box-border {{ stroke: {d.border}; stroke-width: 1.5; fill: none; }}
    .mdview-diagram .box-separator {{ stroke: {d.border}; stroke-width: 1; }}
    .mdview-diagram .box-text {{ fill: {d.fg}; white-space: pre; }}
    .mdview-diagram .box-header {{ fill: {d.header_text}; font-weight: 600; }}
    .mdview-diagram .arrow-line {{ stroke: {d.arrow}; stroke-width: 1.5; fill: none; }}
    .mdview-diagram .arrow-head {{ fill: {d.arrow}; stroke: none; }}
    .mdview-diagram .arrow-label {{ fill: {d.label}; font-size: 12px; text-anchor: middle; }}
    .mdview-diagram .arrow-label-bg {{ fill: {d.bg}; fill-opacity: 0.85; rx: 3; }}
    .mdview-diagram .bg {{ fill: {d.bg}; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .box-border {{ stroke: {l.border}; }}
      .mdview-diagram .box-separator {{ stroke: {l.border}; }}
      .mdview-diagram .box-text {{ fill: {l.fg}; }}
      .mdview-diagram .box-header {{ fill: {l.header_text}; }}
      .mdview-diagram .arrow-line {{ stroke: {l.arrow}; }}
      .mdview-diagram .arrow-head {{ fill: {l.arrow}; }}
      .mdview-diagram .arrow-label {{ fill: {l.label}; }}
      .mdview-diagram .arrow-label-bg {{ fill: {l.bg}; fill-opacity: 0.85; }}
      .mdview-diagram .bg {{ fill: {l.bg}; }}
    }}
  </style>"""

    def table_css(self) -> str:
        """Generate table-specific CSS additions."""
        d = self.dark
        l = self.light
        return f"""  <style>
    .mdview-diagram .table-header-bg {{ fill: {d.bg_secondary}; }}
    .mdview-diagram .table-cell-bg {{ fill: none; }}
    .mdview-diagram .table-border {{ stroke: {d.border}; stroke-width: 1; fill: none; }}
    .mdview-diagram .table-header-text {{ fill: {d.header_text}; font-weight: 600; white-space: pre; }}
    .mdview-diagram .table-cell-text {{ fill: {d.fg}; white-space: pre; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .table-header-bg {{ fill: {l.bg_secondary}; }}
      .mdview-diagram .table-border {{ stroke: {l.border}; }}
      .mdview-diagram .table-header-text {{ fill: {l.header_text}; }}
      .mdview-diagram .table-cell-text {{ fill: {l.fg}; }}
    }}
  </style>"""

    def sequence_css(self) -> str:
        """Generate sequence diagram CSS."""
        d = self.dark
        l = self.light
        return f"""  <style>
    .mdview-diagram {{ font-family: {self.font_family}; font-size: {self.font_size}; }}
    .mdview-diagram .bg {{ fill: {d.bg}; }}
    .mdview-diagram .actor-box {{ fill: {d.bg_secondary}; stroke: {d.border}; stroke-width: 1.5; }}
    .mdview-diagram .actor-text {{ fill: {d.header_text}; font-weight: 600; text-anchor: middle; dominant-baseline: central; }}
    .mdview-diagram .lifeline {{ stroke: {d.muted}; stroke-width: 1; stroke-dasharray: 6,4; }}
    .mdview-diagram .msg-line {{ stroke: {d.arrow}; stroke-width: 1.5; fill: none; }}
    .mdview-diagram .msg-head {{ fill: {d.arrow}; stroke: none; }}
    .mdview-diagram .msg-label {{ fill: {d.label}; font-size: 12px; text-anchor: middle; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .bg {{ fill: {l.bg}; }}
      .mdview-diagram .actor-box {{ fill: {l.bg_secondary}; stroke: {l.border}; }}
      .mdview-diagram .actor-text {{ fill: {l.header_text}; }}
      .mdview-diagram .lifeline {{ stroke: {l.muted}; }}
      .mdview-diagram .msg-line {{ stroke: {l.arrow}; }}
      .mdview-diagram .msg-head {{ fill: {l.arrow}; }}
      .mdview-diagram .msg-label {{ fill: {l.label}; }}
    }}
  </style>"""


# ── Built-in themes ───────────────────────────────────────────────────

TOKYONIGHT = Theme(
    name="tokyonight",
    dark=ThemeColors(
        bg="#1a1b26",
        bg_secondary="#24283b",
        fg="#a9b1d6",
        heading="#7aa2f7",
        header_text="#9ece6a",
        label="#e0af68",
        border="#7aa2f7",
        separator="#7aa2f7",
        muted="#565f89",
        arrow="#bb9af7",
        arrow_label_bg="#1a1b26",
    ),
    light=ThemeColors(
        bg="#f8f8fc",
        bg_secondary="#e8e8f0",
        fg="#343b58",
        heading="#2e7de9",
        header_text="#587539",
        label="#8c6c3e",
        border="#2e7de9",
        separator="#2e7de9",
        muted="#9ca0b0",
        arrow="#7847bd",
        arrow_label_bg="#f8f8fc",
    ),
)

BUILTIN_THEMES: dict[str, Theme] = {
    "tokyonight": TOKYONIGHT,
}

# Default theme used when none specified
DEFAULT_THEME = TOKYONIGHT


# ── Theme loading ─────────────────────────────────────────────────────

_CONFIG_DIR = Path.home() / ".config" / "mdview" / "themes"


def load_theme(name: str) -> Theme:
    """Load a theme by name.

    Checks built-in themes first, then ~/.config/mdview/themes/{name}.yaml.
    Falls back to tokyonight if not found.
    """
    if name in BUILTIN_THEMES:
        return BUILTIN_THEMES[name]

    theme_file = _CONFIG_DIR / f"{name}.yaml"
    if theme_file.exists():
        return _load_yaml_theme(theme_file, name)

    return DEFAULT_THEME


def _load_yaml_theme(path: Path, name: str) -> Theme:
    """Load a theme from a YAML file.

    Expected format:
        dark:
          bg: "#1a1b26"
          bg_secondary: "#24283b"
          fg: "#a9b1d6"
          ...
        light:
          bg: "#f8f8fc"
          ...
        font_family: "..." (optional)
        font_size: "13px" (optional)
    """
    try:
        import yaml
    except ImportError:
        return DEFAULT_THEME

    try:
        data = yaml.safe_load(path.read_text())
    except Exception:
        return DEFAULT_THEME

    if not isinstance(data, dict) or "dark" not in data:
        return DEFAULT_THEME

    def colors_from_dict(d: dict) -> ThemeColors:
        # Fill missing keys from tokyonight defaults
        defaults = TOKYONIGHT.dark
        return ThemeColors(
            bg=d.get("bg", defaults.bg),
            bg_secondary=d.get("bg_secondary", defaults.bg_secondary),
            fg=d.get("fg", defaults.fg),
            heading=d.get("heading", defaults.heading),
            header_text=d.get("header_text", defaults.header_text),
            label=d.get("label", defaults.label),
            border=d.get("border", defaults.border),
            separator=d.get("separator", defaults.separator),
            muted=d.get("muted", defaults.muted),
            arrow=d.get("arrow", defaults.arrow),
            arrow_label_bg=d.get("arrow_label_bg", defaults.arrow_label_bg),
        )

    dark = colors_from_dict(data["dark"])
    light_data = data.get("light", data["dark"])
    light = colors_from_dict(light_data)

    return Theme(
        name=name,
        dark=dark,
        light=light,
        font_family=data.get("font_family", TOKYONIGHT.font_family),
        font_size=data.get("font_size", TOKYONIGHT.font_size),
    )
