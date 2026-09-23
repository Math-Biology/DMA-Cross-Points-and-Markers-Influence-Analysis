# LINKED-TO: [REQ-CPM-IA-P26.0001]
"""Unit tests for src/config_loader.py — TC-01-001 through TC-01-015."""

from pathlib import Path

import pytest

from src.config_loader import (
    CpmIaConfig,
    ConfigurationError,
    CsvInputConfig,
    DataQualityConfig,
    ExcelFileConfig,
    ExcelInputConfig,
    InputConfig,
    load_config,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_XML_NEW_STYLE = """<cpm_ia_config>
  <input>
    <type>csv</type>
    <csv><path>/data/input/raw_variation.csv</path></csv>
  </input>
  <output_path>/data/output</output_path>
  <output_label_detail>cpm_detail</output_label_detail>
  <output_label_aggregated>cpm_aggregated</output_label_aggregated>
  <threshold_pct>350.0</threshold_pct>
  <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
  <n_max>10</n_max>
</cpm_ia_config>"""

_VALID_XML_LEGACY = """<cpm_ia_config>
    <input_path>/data/input/raw_variation.csv</input_path>
    <output_path>/data/output</output_path>
    <output_label_detail>cpm_detail</output_label_detail>
    <output_label_aggregated>cpm_aggregated</output_label_aggregated>
    <threshold_pct>350.0</threshold_pct>
    <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    <n_max>10</n_max>
</cpm_ia_config>"""


def _write(tmp_path, content, name="config.xml"):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_tc_01_001_new_style_csv_valid(tmp_path):
    """New-style XML with <input><type>csv</type></input> returns correct CpmIaConfig."""
    cfg = load_config(_write(tmp_path, _VALID_XML_NEW_STYLE))
    assert isinstance(cfg, CpmIaConfig)
    assert cfg.input.type == "csv"
    assert cfg.input.csv is not None
    assert cfg.input.csv.path == Path("/data/input/raw_variation.csv")
    assert cfg.output_path == Path("/data/output")
    assert cfg.threshold_pct == 350.0
    assert cfg.rise_tolerance_epsilon == 5.0
    assert cfg.n_max == 10


def test_tc_01_001_config_is_immutable(tmp_path):
    cfg = load_config(_write(tmp_path, _VALID_XML_NEW_STYLE))
    with pytest.raises(Exception):
        cfg.n_max = 99


def test_tc_01_002_legacy_input_path_creates_csv_input(tmp_path):
    """Legacy <input_path> tag creates InputConfig(type='csv', csv=...) transparently."""
    cfg = load_config(_write(tmp_path, _VALID_XML_LEGACY))
    assert cfg.input.type == "csv"
    assert cfg.input.csv is not None
    assert cfg.input.csv.path == Path("/data/input/raw_variation.csv")
    assert cfg.input.excel is None
    assert cfg.input.db is None


def test_tc_01_002_legacy_threshold_present(tmp_path):
    cfg = load_config(_write(tmp_path, _VALID_XML_LEGACY))
    assert cfg.threshold_pct == 350.0


def test_tc_01_003_file_not_found(tmp_path):
    with pytest.raises(ConfigurationError, match="not found"):
        load_config(tmp_path / "missing.xml")


def test_tc_01_004_malformed_xml(tmp_path):
    p = _write(tmp_path, "<cpm_ia_config><input><type>csv</type></input>")
    with pytest.raises(ConfigurationError, match="Malformed XML"):
        load_config(p)


def test_tc_01_004_empty_file(tmp_path):
    p = _write(tmp_path, "")
    with pytest.raises(ConfigurationError):
        load_config(p)


def test_tc_01_005_n_max_missing(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


def test_tc_01_005_rise_tolerance_missing(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="rise_tolerance_epsilon"):
        load_config(_write(tmp_path, xml))


def test_tc_01_006_n_max_non_integer(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>abc</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


def test_tc_01_006_n_max_float_string_rejected(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10.0</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="n_max"):
        load_config(_write(tmp_path, xml))


def test_tc_01_007_threshold_pct_malformed(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>not_a_number</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="threshold_pct"):
        load_config(_write(tmp_path, xml))


def test_tc_01_008_threshold_pct_absent_raises(tmp_path):
    """threshold_pct absent raises ConfigurationError (now required, no silent default)."""
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="threshold_pct"):
        load_config(_write(tmp_path, xml))


def test_tc_01_009_blank_output_label_detail(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/data/input/f.csv</path></csv></input>
        <output_path>/data/output</output_path>
        <output_label_detail>   </output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError, match="output_label_detail"):
        load_config(_write(tmp_path, xml))


def test_tc_01_010_no_input_block_raises(tmp_path):
    """Neither <input> nor <input_path> present raises ConfigurationError."""
    xml = """<cpm_ia_config>
        <output_path>/data/output</output_path>
        <output_label_detail>cpm_detail</output_label_detail>
        <output_label_aggregated>cpm_aggregated</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
    </cpm_ia_config>"""
    with pytest.raises(ConfigurationError):
        load_config(_write(tmp_path, xml))


def test_tc_01_011_excel_input_type(tmp_path):
    xml = """<cpm_ia_config>
      <input>
        <type>excel</type>
        <excel>
          <file>
            <path>data/input/visit1.xlsx</path>
            <visit_id>V001</visit_id>
            <visit_date>2026-01-01</visit_date>
          </file>
          <file>
            <path>data/input/visit2.xlsx</path>
            <visit_id>V002</visit_id>
            <visit_date>2026-02-01</visit_date>
          </file>
        </excel>
      </input>
      <output_path>/data/output</output_path>
      <output_label_detail>cpm_detail</output_label_detail>
      <output_label_aggregated>cpm_aggregated</output_label_aggregated>
      <threshold_pct>300.0</threshold_pct>
      <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
      <n_max>10</n_max>
    </cpm_ia_config>"""
    cfg = load_config(_write(tmp_path, xml))
    assert cfg.input.type == "excel"
    assert cfg.input.excel is not None
    assert len(cfg.input.excel.files) == 2
    assert cfg.input.excel.files[0].visit_id == "V001"
    assert cfg.input.excel.files[1].visit_id == "V002"
    assert cfg.input.excel.files[0].path == Path("data/input/visit1.xlsx")


def test_tc_01_012_data_quality_drop_true(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/f.csv</path></csv></input>
        <output_path>/out</output_path>
        <output_label_detail>d</output_label_detail>
        <output_label_aggregated>a</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
        <data_quality><drop_invalid_points>true</drop_invalid_points></data_quality>
    </cpm_ia_config>"""
    cfg = load_config(_write(tmp_path, xml))
    assert cfg.data_quality.drop_invalid_points is True


def test_tc_01_012_data_quality_drop_false(tmp_path):
    xml = """<cpm_ia_config>
        <input><type>csv</type><csv><path>/f.csv</path></csv></input>
        <output_path>/out</output_path>
        <output_label_detail>d</output_label_detail>
        <output_label_aggregated>a</output_label_aggregated>
        <threshold_pct>300.0</threshold_pct>
        <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
        <n_max>10</n_max>
        <data_quality><drop_invalid_points>false</drop_invalid_points></data_quality>
    </cpm_ia_config>"""
    cfg = load_config(_write(tmp_path, xml))
    assert cfg.data_quality.drop_invalid_points is False


def test_tc_01_012_data_quality_absent_defaults_true(tmp_path):
    cfg = load_config(_write(tmp_path, _VALID_XML_NEW_STYLE))
    assert cfg.data_quality.drop_invalid_points is True


def test_tc_01_013_input_description_csv(tmp_path):
    cfg = load_config(_write(tmp_path, _VALID_XML_NEW_STYLE))
    desc = cfg.input_description()
    assert "/data/input/raw_variation.csv" in desc


def test_tc_01_013_input_description_excel(tmp_path):
    xml = """<cpm_ia_config>
      <input>
        <type>excel</type>
        <excel>
          <file><path>f.xlsx</path><visit_id>V1</visit_id><visit_date>2026-01-01</visit_date></file>
        </excel>
      </input>
      <output_path>/out</output_path>
      <output_label_detail>d</output_label_detail>
      <output_label_aggregated>a</output_label_aggregated>
      <threshold_pct>300.0</threshold_pct>
      <rise_tolerance_epsilon>5.0</rise_tolerance_epsilon>
      <n_max>10</n_max>
    </cpm_ia_config>"""
    cfg = load_config(_write(tmp_path, xml))
    desc = cfg.input_description()
    assert "excel" in desc
    assert "1 file(s)" in desc
