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
from typing import Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigurationError(Exception):
    """Raised when the XML config file is missing, malformed, or contains invalid values."""


# ---------------------------------------------------------------------------
# Input configuration dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CsvInputConfig:
    path: Path


@dataclass(frozen=True)
class ExcelFileConfig:
    path: Path
    visit_id: str
    visit_date: str


@dataclass(frozen=True)
class ExcelInputConfig:
    files: tuple  # Tuple[ExcelFileConfig, ...]


@dataclass(frozen=True)
class DbInputConfig:
    dsn_env: str
    query: str


@dataclass(frozen=True)
class InputConfig:
    type: str  # 'csv' | 'excel' | 'db'
    csv: Optional[CsvInputConfig]
    excel: Optional[ExcelInputConfig]
    db: Optional[DbInputConfig]


@dataclass(frozen=True)
class DataQualityConfig:
    drop_invalid_points: bool


@dataclass(frozen=True)
class CpmIaConfig:
    """Immutable container for all CPM-IA runtime parameters.

    Populated exclusively by load_config(); never constructed directly by other modules.
    """

    input: InputConfig
    output_path: Path
    output_label_detail: str
    output_label_aggregated: str
    threshold_pct: float
    rise_tolerance_epsilon: float
    n_max: int
    data_quality: DataQualityConfig

    def input_description(self) -> str:
        """Human-readable input description for the report."""
        if self.input.type == 'csv':
            return str(self.input.csv.path)
        elif self.input.type == 'excel':
            return f"excel [{len(self.input.excel.files)} file(s)]"
        elif self.input.type == 'db':
            return f"db [dsn_env={self.input.db.dsn_env}]"
        return "unknown"


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


def _parse_input_block(root: ET.Element) -> InputConfig:
    """Parse the new-style <input> block."""
    input_elem = root.find("input")
    if input_elem is None:
        raise ConfigurationError("Missing required config element: <input>")

    type_elem = input_elem.find("type")
    if type_elem is None or not (type_elem.text or "").strip():
        raise ConfigurationError("Missing required <type> inside <input>")
    input_type = type_elem.text.strip()

    # Parse CSV sub-config
    csv_cfg: Optional[CsvInputConfig] = None
    csv_elem = input_elem.find("csv")
    if csv_elem is not None:
        path_elem = csv_elem.find("path")
        if path_elem is not None and (path_elem.text or "").strip():
            csv_cfg = CsvInputConfig(path=Path(path_elem.text.strip()))

    # Parse Excel sub-config
    excel_cfg: Optional[ExcelInputConfig] = None
    excel_elem = input_elem.find("excel")
    if excel_elem is not None:
        file_configs = []
        for file_elem in excel_elem.findall("file"):
            path_e = file_elem.find("path")
            vid_e = file_elem.find("visit_id")
            vdate_e = file_elem.find("visit_date")
            if path_e is None or vid_e is None or vdate_e is None:
                raise ConfigurationError(
                    "Each <file> in <excel> must have <path>, <visit_id>, <visit_date>"
                )
            file_configs.append(ExcelFileConfig(
                path=Path(path_e.text.strip()),
                visit_id=vid_e.text.strip(),
                visit_date=vdate_e.text.strip(),
            ))
        excel_cfg = ExcelInputConfig(files=tuple(file_configs))

    # Parse DB sub-config
    db_cfg: Optional[DbInputConfig] = None
    db_elem = input_elem.find("db")
    if db_elem is not None:
        dsn_e = db_elem.find("dsn_env")
        query_e = db_elem.find("query")
        dsn = (dsn_e.text or "").strip() if dsn_e is not None else ""
        query = (query_e.text or "").strip() if query_e is not None else ""
        db_cfg = DbInputConfig(dsn_env=dsn, query=query)

    return InputConfig(type=input_type, csv=csv_cfg, excel=excel_cfg, db=db_cfg)


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

    # Input resolution: new-style <input> block takes priority; fall back to legacy <input_path>
    if root.find("input") is not None:
        input_cfg = _parse_input_block(root)
    elif root.find("input_path") is not None:
        legacy_path = Path(_get_required(root, "input_path", str, "str"))
        input_cfg = InputConfig(
            type="csv",
            csv=CsvInputConfig(path=legacy_path),
            excel=None,
            db=None,
        )
    else:
        raise ConfigurationError(
            "Missing required config element: either <input> or <input_path> must be present"
        )

    # Data quality config (optional block, default drop_invalid_points=True)
    dq_elem = root.find("data_quality")
    if dq_elem is not None:
        drop_elem = dq_elem.find("drop_invalid_points")
        if drop_elem is not None and (drop_elem.text or "").strip():
            drop_val = drop_elem.text.strip().lower() in ("true", "1", "yes")
        else:
            drop_val = True
    else:
        drop_val = True
    data_quality_cfg = DataQualityConfig(drop_invalid_points=drop_val)

    config = CpmIaConfig(
        input=input_cfg,
        output_path=Path(_get_required(root, "output_path", str, "str")),
        output_label_detail=_get_required(root, "output_label_detail", str, "str"),
        output_label_aggregated=_get_required(root, "output_label_aggregated", str, "str"),
        threshold_pct=_get_required(root, "threshold_pct", float, "float"),
        rise_tolerance_epsilon=_get_required(root, "rise_tolerance_epsilon", float, "float"),
        n_max=_get_required(root, "n_max", int, "int"),
        data_quality=data_quality_cfg,
    )

    logger.info(
        "CPM-IA config loaded | input=%s | output=%s | threshold_pct=%.1f | epsilon=%s | n_max=%d",
        config.input_description(),
        config.output_path,
        config.threshold_pct,
        config.rise_tolerance_epsilon,
        config.n_max,
    )

    return config
