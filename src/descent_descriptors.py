# LINKED-TO: [REQ-CPM-IA-P26.0008]
"""
descent_descriptors.py — Descent Shape Descriptors for the CPM-IA component.

Computes three mandatory shape descriptors for each descent window (REQ-CPM-IA-P26.0008):
  - descent_depth:          anchor_value − min(window_values)
  - descent_length:         number of points in the window
  - mean_per_step_decrease: depth / (length − 1)  [0.0 when length == 1]

Anchor value is sourced from trigger_results (Module 04); window from Module 06.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from src.descent_window import DescentWindow, DescentWindows
from src.trigger_detection import TriggerResults

logger = logging.getLogger(__name__)


class DescriptorError(Exception):
    """Raised when descriptor computation encounters missing anchor or NaN values."""


@dataclass(frozen=True)
class DescentDescriptor:
    """Immutable shape descriptors for one (visit, point) descent window."""

    descent_depth: float           # anchor_value - min(window_values); >= 0
    descent_length: int            # == window.window_length
    mean_per_step_decrease: float  # depth / (length-1), or 0.0 when length == 1


Descriptors = Dict[Tuple[str, str], Optional[DescentDescriptor]]


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _compute_descriptor(
    window: DescentWindow,
    anchor_value: float,
    key: Tuple[str, str],
) -> DescentDescriptor:
    """Compute the three shape descriptors for a single descent window."""
    if any(math.isnan(v) for v in window.window_values):
        raise DescriptorError(
            f"NaN in descent window for {key}"
        )

    depth = anchor_value - min(window.window_values)
    length = window.window_length
    mean_per_step = depth / (length - 1) if length > 1 else 0.0

    return DescentDescriptor(
        descent_depth=depth,
        descent_length=length,
        mean_per_step_decrease=mean_per_step,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_descriptors(
    descent_windows: DescentWindows,
    trigger_results: TriggerResults,
) -> Descriptors:
    """
    Compute descent shape descriptors for every (visit, point) series.

    Args:
        descent_windows: Mapping (visit_id, point_id) -> DescentWindow | None
                         from determine_descent_windows().
        trigger_results: Mapping (visit_id, point_id) -> TriggerResult
                         from detect_triggers().

    Returns:
        Descriptors: mapping (visit_id, point_id) -> DescentDescriptor or None.
        None is returned for series with no descent window.

    Raises:
        DescriptorError: if a non-None window has a missing anchor value, or if
        a window contains NaN (should not occur with valid upstream data).
    """
    descriptors: Descriptors = {}

    for key, window in descent_windows.items():
        if window is None:
            descriptors[key] = None
            continue

        anchor_value = trigger_results[key].first_positive_value
        if anchor_value is None:
            raise DescriptorError(
                f"Anchor value missing for {key} with a non-None descent window"
            )

        descriptors[key] = _compute_descriptor(window, anchor_value, key)

    logger.debug(
        "CPM-IA descriptors computed | total=%d | with_descriptor=%d | none=%d",
        len(descriptors),
        sum(1 for d in descriptors.values() if d is not None),
        sum(1 for d in descriptors.values() if d is None),
    )

    return descriptors
