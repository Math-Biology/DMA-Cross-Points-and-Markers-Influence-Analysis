# LINKED-TO: [REQ-CPM-IA-P26.0001]
"""Unit tests for src/config_loader.py — TC-01-001 through TC-01-008."""

from pathlib import Path

import pytest

from src.config_loader import CpmIaConfig, ConfigurationError, load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_XML = """<cpm_ia_config>
    <input_path>/data/input/raw_variation.csv</input_path>
    <output_path>/data/output</output_path>
    <output_label_detail>cpm_detail</output_label_detail>
    <output_label_aggregated>cpm_aggregated</output_label_aggregated>
    <threshold_pct>350.0</threshold_pct>
    <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    <n_max>10</n_max>
</cpm_ia_config>"""


def _write(tmp_path: Path, content: str, name: str = "config.xml") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# TC-01-001 — All required fields present
# ---------------------------------------------------------------------------

def test_tc_01_001_valid_all_fields(tmp_path: Path) -> None:
    """Valid XML with all 7 fields returns a correctly populated CpmIaConfig."""
    cfg = load_config(_write(tmp_path, _VALID_XML))

    assert isinstance(cfg, CpmIaConfig)
    assert cfg.input_path == Path("/data/input/raw_variation.csv")
    assert cfg.output_path == Path("/data/output")
    assert cfg.output_label_detail == "cpm_detail"
    assert cfg.output_label_aggregated == "cpm_aggregated"
    assert cfg.threshold_pct == 350.0
    assert cfg.rise_tolerance_epsilon == 5.0
    assert cfg.n_max == 10


def test_tc_01_001_config_is_immutable(tmp_path: Path) -> None:
    """CpmIaConfig must be immutable (frozen dataclass)."""
    cfg = load_config(_write(tmp_path, _VALID_XML))
    with pytest.raises(Exception):
        cfg.n_max = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TC-01-002 — threshold_pct absent -> default 300.0
# ---------------------------------------------------------------------------

def test_tc_01_002_threshold_absent_defaults_to_300(tmp_path: Path) -> None:
    """threshold_pct element absent: CpmIaConfig.threshold_pct == 300.0."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    cfg = load_config(_write(tmp_path, xml))
    assert cfg.threshold_pct == 300.0


# ---------------------------------------------------------------------------
# TC-01-003 — File not found
# ---------------------------------------------------------------------------

def test_tc_01_003_file_not_found(tmp_path: Path) -> None:
    """Non-existent path raises ConfigurationError mentioning 'not found'."""
    with pytest.raises(ConfigurationError, match="not found"):
        load_config(tmp_path / "missing.xml")


# ---------------------------------------------------------------------------
# TC-01-004 — Malformed XML
# ---------------------------------------------------------------------------

def test_tc_01_004_malformed_xml(tmp_path: Path) -> None:
    """Truncated XML raises ConfigurationError mentioning 'Malformed XML'."""
    p = _write(tmp_path, "<cpm_ia_config><input_path>foo</input_path>")
    with pytest.raises(ConfigurationError, match="Malformed XML"):
        load_config(p)


def test_tc_01_004_empty_file(tmp_path: Path) -> None:
    """Empty file raises ConfigurationError (not a valid XML document)."""
    p = _write(tmp_path, "")
    with pytest.raises(ConfigurationError):
        load_config(p)


# ---------------------------------------------------------------------------
# TC-01-005 — Required element missing
# ---------------------------------------------------------------------------

def test_tc_01_005_n_max_missing(tmp_path: Path) -> None:
    """n_max element absent raises ConfigurationError naming the tag."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


def test_tc_01_005_rise_tolerance_missing(tmp_path: Path) -> None:
    """rise_tolerance_epsilon absent raises ConfigurationError."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="rise_tolerance_epsilon"):
        load_config(_write(tmp_path, xml))


# ---------------------------------------------------------------------------
# TC-01-006 — n_max non-integer value
# ---------------------------------------------------------------------------

def test_tc_01_006_n_max_non_integer(tmp_path: Path) -> None:
    """n_max = 'abc' raises ConfigurationError naming n_max and int."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>abc</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


def test_tc_01_006_n_max_float_string_rejected(tmp_path: Path) -> None:
    """n_max = '10.0' (float-like string) raises ConfigurationError; int cast is strict."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10.0</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


# ---------------------------------------------------------------------------
# TC-01-007 — Optional field present but malformed
# ---------------------------------------------------------------------------

def test_tc_01_007_threshold_pct_malformed(tmp_path: Path) -> None:
    """threshold_pct present but non-float raises ConfigurationError."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>not_a_number</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="threshold_pct"):
        load_config(_write(tmp_path, xml))


# ---------------------------------------------------------------------------
# TC-01-008 — Required string present but blank
# ---------------------------------------------------------------------------

def test_tc_01_008_blank_output_label_detail(tmp_path: Path) -> None:
    """output_label_detail whitespace-only raises ConfigurationError."""
    xml = """<cpm_ia_config>
        <input_path>/data/input/raw_variation.csv</input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>   </output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="output_label_detail"):
        load_config(_write(tmp_path, xml))


def test_tc_01_008_empty_input_path(tmp_path: Path) -> None:
    """input_path element present but empty raises ConfigurationError."""
    xml = """<cpm_ia_config>
        <input_path></input_path>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="input_path"):
        load_config(_write(tmp_path, xml))
