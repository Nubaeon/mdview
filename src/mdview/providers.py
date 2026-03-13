"""AI provider interface for diagram interpretation.

Pluggable backends that take ASCII art and return a DiagramSpec.
Configured via mdview.yaml — provider-agnostic like embedding model configs.

Providers:
- anthropic: Claude API (haiku recommended for speed)
- openai: OpenAI API (gpt-4o-mini recommended)
- ollama: Local models via Ollama (llama3.2, phi-3, etc.)
- none: No AI — fall back to heuristic rendering
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from .config import AIConfig
from .spec import DiagramSpec, validate_spec

logger = logging.getLogger(__name__)

# The prompt that converts ASCII art to DiagramSpec JSON.
# Shared across all providers — only the API call differs.
INTERPRETATION_PROMPT = '''You are a diagram interpreter. Given ASCII art, output a JSON DiagramSpec.

## Schema

```json
{
  "type": "flow|sequence|wireframe|table|box",
  "title": "optional title",
  "layout": "horizontal|vertical|grid|nested|sequence|auto",
  "elements": [
    {
      "id": "unique_id",
      "label": "display text",
      "type": "node|actor|panel|input|header|row|box|decision|sidebar|form",
      "children": ["child_id1"],
      "properties": {}
    }
  ],
  "connections": [
    {
      "from": "element_id",
      "to": "element_id",
      "label": "optional label",
      "style": "solid|dashed",
      "properties": {}
    }
  ],
  "properties": {}
}
```

## Type guide

- **flow**: Boxes connected by arrows. Elements are nodes/decisions. Connections have labels.
- **sequence**: Actors with messages between them (top-to-bottom ordering). Elements are actors. Connections have order property.
- **wireframe**: Nested panels with UI elements. Use children for nesting. Elements can be panel, sidebar, input, form.
- **table**: Header row + data rows. Elements are header/row type with cells in properties.
- **box**: Simple boxes with optional sections (separated by horizontal lines). Use properties.sections for multi-section boxes.

## Rules

1. Output ONLY valid JSON — no markdown, no explanation
2. Every element needs a unique id (use short descriptive names like "client", "nav_panel")
3. For sequence diagrams, add {"order": N} to connection properties (1-based)
4. For tables, use {"cells": ["col1", "col2"]} in element properties
5. For wireframes, nest elements via children arrays
6. Infer layout from the visual arrangement (horizontal if side-by-side, vertical if stacked)

## ASCII art to interpret:

'''


class DiagramProvider(ABC):
    """Abstract base for diagram interpretation providers."""

    @abstractmethod
    def interpret(self, source: str) -> DiagramSpec | None:
        """Interpret ASCII art and return a DiagramSpec, or None on failure."""
        ...


class AnthropicProvider(DiagramProvider):
    """Claude API provider."""

    def __init__(self, config: AIConfig):
        self.model = config.model or "claude-haiku-4-5-20251001"
        self.api_key = config.api_key
        self.timeout = config.timeout
        self.base_url = config.base_url or "https://api.anthropic.com"

    def interpret(self, source: str) -> DiagramSpec | None:
        if not self.api_key:
            logger.warning("Anthropic API key not set")
            return None

        body = json.dumps({
            "model": self.model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": INTERPRETATION_PROMPT + source}],
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        return self._call(req)

    def _call(self, req: urllib.request.Request) -> DiagramSpec | None:
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            data = json.loads(resp.read().decode("utf-8"))
            text = data["content"][0]["text"]
            return _parse_spec_response(text)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logger.warning(f"Anthropic API error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse Anthropic response: {e}")
            return None


class OpenAIProvider(DiagramProvider):
    """OpenAI-compatible API provider (works with OpenAI, Azure, etc.)."""

    def __init__(self, config: AIConfig):
        self.model = config.model or "gpt-4o-mini"
        self.api_key = config.api_key
        self.timeout = config.timeout
        self.base_url = config.base_url or "https://api.openai.com/v1"

    def interpret(self, source: str) -> DiagramSpec | None:
        if not self.api_key:
            logger.warning("OpenAI API key not set")
            return None

        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": INTERPRETATION_PROMPT + source},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            data = json.loads(resp.read().decode("utf-8"))
            text = data["choices"][0]["message"]["content"]
            return _parse_spec_response(text)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logger.warning(f"OpenAI API error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse OpenAI response: {e}")
            return None


class OllamaProvider(DiagramProvider):
    """Local Ollama provider — no API key needed."""

    def __init__(self, config: AIConfig):
        self.model = config.model or "llama3.2"
        self.timeout = config.timeout
        self.base_url = config.base_url or "http://localhost:11434"

    def interpret(self, source: str) -> DiagramSpec | None:
        body = json.dumps({
            "model": self.model,
            "prompt": INTERPRETATION_PROMPT + source,
            "stream": False,
            "format": "json",
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            data = json.loads(resp.read().decode("utf-8"))
            text = data["response"]
            return _parse_spec_response(text)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logger.warning(f"Ollama API error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse Ollama response: {e}")
            return None


# ── Provider factory ──────────────────────────────────────────────

_PROVIDERS: dict[str, type[DiagramProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def create_provider(config: AIConfig) -> DiagramProvider | None:
    """Create a provider from config. Returns None if provider is 'none' or unknown."""
    if config.provider == "none" or not config.provider:
        return None

    provider_cls = _PROVIDERS.get(config.provider)
    if provider_cls is None:
        logger.warning(f"Unknown AI provider: {config.provider!r}")
        return None

    return provider_cls(config)


# ── Response parsing ──────────────────────────────────────────────

def _parse_spec_response(text: str) -> DiagramSpec | None:
    """Parse LLM response text into a DiagramSpec.

    Handles JSON wrapped in markdown code fences or bare JSON.
    """
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        spec = DiagramSpec.from_json(text)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse DiagramSpec from LLM response: {e}")
        return None

    errors = validate_spec(spec)
    if errors:
        logger.warning(f"DiagramSpec validation errors: {errors}")
        # Return it anyway — partial specs can still render
    return spec
