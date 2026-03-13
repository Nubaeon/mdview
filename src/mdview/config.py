"""Configuration system for mdview.

Loads from mdview.yaml (project-level) or ~/.config/mdview/config.yaml (global).
Project-level config takes precedence over global.

AI backend is configured like embedding models — set the provider, model,
and point to the API key via environment variable name.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Config search paths (project-level first, then global)
_CONFIG_NAMES = ["mdview.yaml", "mdview.yml"]
_GLOBAL_CONFIG_DIR = Path.home() / ".config" / "mdview"


@dataclass
class AIConfig:
    """AI backend configuration."""

    provider: str = "none"  # "anthropic", "openai", "ollama", "none"
    model: str = ""  # e.g. "claude-haiku-4-5", "gpt-4o-mini", "llama3.2"
    api_key_env: str = ""  # env var name containing the API key
    base_url: str = ""  # override for ollama or custom endpoints
    timeout: int = 30  # request timeout in seconds

    @property
    def api_key(self) -> str | None:
        """Resolve API key from environment variable."""
        if self.api_key_env:
            return os.environ.get(self.api_key_env)
        # Auto-detect common env vars per provider
        auto_vars = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        var = auto_vars.get(self.provider, "")
        return os.environ.get(var) if var else None

    @property
    def is_configured(self) -> bool:
        """Check if an AI backend is configured and has credentials."""
        if self.provider == "none":
            return False
        if self.provider == "ollama":
            return True  # ollama doesn't need API keys
        return self.api_key is not None


@dataclass
class DiagramConfig:
    """Diagram rendering configuration."""

    fallback: str = "heuristic"  # "heuristic", "svgbob", "none"
    types: list[str] = field(
        default_factory=lambda: ["flow", "sequence", "wireframe", "table", "box"]
    )


@dataclass
class MdviewConfig:
    """Top-level mdview configuration."""

    ai: AIConfig = field(default_factory=AIConfig)
    theme: str = "tokyo-night"  # theme name
    diagrams: DiagramConfig = field(default_factory=DiagramConfig)

    @classmethod
    def load(cls, project_dir: str | Path | None = None) -> MdviewConfig:
        """Load config from yaml file.

        Search order:
        1. project_dir/mdview.yaml (if project_dir given)
        2. cwd/mdview.yaml
        3. ~/.config/mdview/config.yaml
        4. defaults
        """
        search_paths: list[Path] = []

        if project_dir:
            for name in _CONFIG_NAMES:
                search_paths.append(Path(project_dir) / name)

        for name in _CONFIG_NAMES:
            search_paths.append(Path.cwd() / name)

        search_paths.append(_GLOBAL_CONFIG_DIR / "config.yaml")
        search_paths.append(_GLOBAL_CONFIG_DIR / "config.yml")

        for path in search_paths:
            if path.is_file():
                return cls._load_from_file(path)

        return cls()  # defaults

    @classmethod
    def _load_from_file(cls, path: Path) -> MdviewConfig:
        """Load config from a YAML file."""
        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed — using default config")
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return cls()

        logger.info(f"Loaded config from {path}")
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> MdviewConfig:
        """Build config from parsed YAML dict."""
        ai_data = data.get("ai", {})
        ai = AIConfig(
            provider=ai_data.get("provider", "none"),
            model=ai_data.get("model", ""),
            api_key_env=ai_data.get("api_key_env", ""),
            base_url=ai_data.get("base_url", ""),
            timeout=ai_data.get("timeout", 30),
        )

        diag_data = data.get("diagrams", {})
        diagrams = DiagramConfig(
            fallback=diag_data.get("fallback", "heuristic"),
            types=diag_data.get("types", DiagramConfig().types),
        )

        return cls(
            ai=ai,
            theme=data.get("theme", "tokyo-night"),
            diagrams=diagrams,
        )
