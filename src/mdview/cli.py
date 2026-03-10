"""mdview CLI — render markdown with diagrams.

Usage:
    mdview FILE.md                  # Open in browser (HTML mode)
    mdview FILE.md --terminal       # Render in terminal
    mdview FILE.md -o output.html   # Write to specific file
    mdview FILE.md --no-open        # Generate HTML without opening
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mdview",
        description="Lightweight markdown + diagram viewer",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Markdown file to render",
    )
    parser.add_argument(
        "--terminal", "-t",
        action="store_true",
        help="Render in terminal (requires rich)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output HTML file path (default: same name with .html)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't open in browser after rendering",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Terminal width (terminal mode only)",
    )
    parser.add_argument(
        "--diagram-service",
        default=None,
        help="Override diagram rendering service URL",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    from .renderer import render_file

    if args.terminal:
        render_file(args.file, format="terminal", width=args.width)
    else:
        output = args.output
        if output is None:
            # Default: same directory, .html extension
            output = args.file.with_suffix(".html")

        render_file(
            args.file,
            format="html",
            output_path=output,
            open_browser=not args.no_open,
        )


def _get_version() -> str:
    try:
        from . import __version__
        return __version__
    except Exception:
        return "0.1.0"


if __name__ == "__main__":
    main()
