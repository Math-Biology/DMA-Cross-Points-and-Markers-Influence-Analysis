# LINKED-TO: [REQ-CPM-IA-P26.0001]
"""
config_loader.py — External Configuration Loading for the CPM-IA component.

Sole entry point for all runtime parameters (G-01). Called once by main.py at
process start; any failure produces a controlled abort with no partial run (G-02).
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigurationError(Exception):
    """Raised when the XML config file is missing, malformed, or contains invalid values."""


@dataclass(frozen=True)
class CpmIaConfig:
    """Immutable container for all CPM-IA runtime parameters.

    Populated exclusively by load_config(); never constructed directly by other modules.
    """

    input_path: Path
    output_path: Path
    output_label_detail: str
    output_label_aggregated: str
    threshold_pct: float
    rise_tolerance_epsilon: float
    n_max: int


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get_required(
    root: ET.Element,
    tag: str,
    cast_fn: Callable[[str], T],
    type_name: str,
) -> T:
    """Extract and cast a required XML element. Raises ConfigurationError on any failure."""
    elem = root.find(tag)
    if elem is None or not (elem.text or "").strip():
        raise ConfigurationError(f"Missing required config element: <{tag}>")
    text = elem.text.strip()  # type: ignore[union-attr]
    try:
        return cast_fn(text)
    except (ValueError, TypeError):
        raise ConfigurationError(
            f"Invalid value for <{tag}>: expected {type_name}, got {text!r}"
        )


def _get_optional(
    root: ET.Element,
    tag: str,
    cast_fn: Callable[[str], T],
    type_name: str,
    default: T,
) -> T:
    """Extract and cast an optional XML element; return *default* if absent or blank.

    Raises ConfigurationError when the element is present but its value cannot be cast.
    """
    elem = root.find(tag)
    if elem is None or not (elem.text or "").strip():
        return default
    text = elem.text.strip()  # type: ignore[union-attr]
    try:
        return cast_fn(text)
    except (ValueError, TypeError):
        raise ConfigurationError(
            f"Invalid value for <{tag}>: expected {type_name}, got {text!r}"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path) -> CpmIaConfig:
    """Parse and validate the XML configuration file at *config_path*.

    Returns a fully populated, immutable CpmIaConfig on success.
    Raises ConfigurationError for any file, parse, or field-validation failure.
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise ConfigurationError(f"Malformed XML in config: {path}") from exc

    root = tree.getroot()

    config = CpmIaConfig(
        input_path=Path(_get_required(root, "input_path", str, "str")),
        output_path=Path(_get_required(root, "output_path", str, "str")),
        output_label_detail=_get_required(root, "output_label_detail", str, "str"),
        output_label_aggregated=_get_required(root, "output_label_aggregated", str, "str"),
        threshold_pct=_get_optional(root, "threshold_pct", float, "float", 300.0),
        rise_tolerance_epsilon=_get_required(root, "rise_tolerance_epsilon", float, "float"),
        n_max=_get_required(root, "n_max", int, "int"),
    )

    logger.info(
        "CPM-IA config loaded | input=%s | output=%s | threshold_pct=%.1f | epsilon=%s | n_max=%d",
        config.input_path,
        config.output_path,
        config.threshold_pct,
        config.rise_tolerance_epsilon,
        config.n_max,
    )

    return config
