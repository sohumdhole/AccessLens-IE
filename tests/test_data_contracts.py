"""Step 7 Tests: Data contracts, provenance manifest, county mapping, DQ rules, and GDPR suppression."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from accesslens.config import (
    ACADEMIC_YEARS,
    CSO_ED_PREFIX_TO_COUNTY,
    DB_PATH,
    INSTITUTION_SECTOR_MAP,
    SMALL_CELL_THRESHOLD,
)


def test_provenance_manifest_complete(repo_root: Path) -> None:
    manifest_path = repo_root / "outputs" / "audit" / "manifest.json"
    assert manifest_path.exists()
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert m["total_raw_files"] == 52
    assert m["total_raw_bytes"] == 620916
    assert len(m["files"]) == 52
    for entry in m["files"]:
        assert entry["bytes"] > 0
        assert len(entry["sha256"]) == 64
        assert entry["source_url"].startswith("https://")
        assert "downloaded_utc" in entry


def test_county_mapping_26_counties(repo_root: Path) -> None:
    df_map = pd.read_csv(repo_root / "outputs" / "kpis" / "county_mapping.csv", dtype=str)
    assert len(df_map) == len(CSO_ED_PREFIX_TO_COUNTY) == 27
    assert df_map["hea_county_name"].nunique() == 26
    assert df_map["hea_county_name"].isna().sum() == 0


def test_dq_rules_all_pass(repo_root: Path) -> None:
    df_dq = pd.read_csv(repo_root / "outputs" / "kpis" / "dq_rule_results.csv")
    assert len(df_dq) == 6
    assert (df_dq["status"] == "PASS").all()
    by_id = df_dq.set_index("rule_id")
    assert int(by_id.loc["DQ01_SUBTOTAL_SEPARATION", "records_flagged_or_quarantined"]) == 6058
    assert int(by_id.loc["DQ02_COUNTY_UNMAPPED_QUARANTINE", "records_flagged_or_quarantined"]) == 14
    assert int(by_id.loc["DQ04_NCI_SCOPE_TRANSITION_FLAG", "records_flagged_or_quarantined"]) == 4
    assert int(by_id.loc["DQ05_POBAL_ED_COUNTY_COMPLETENESS", "records_flagged_or_quarantined"]) == 0
    assert int(by_id.loc["DQ06_SMALL_CELL_SUPPRESSION", "records_flagged_or_quarantined"]) == 206


def test_small_cell_suppression_in_powerbi_dimension_table(repo_root: Path) -> None:
    df_dim = pd.read_csv(repo_root / "outputs" / "powerbi" / "fact_institution_dimension_year.csv")
    assert len(df_dim) == 5874
    # Every non-zero cell belongs to HEA nearest-5 rounding grid
    non_zero = df_dim[df_dim["enrolments"] > 0]
    assert (non_zero["enrolments"] % 5 == 0).all()
    # Every cell 0 < count < 10 must be flagged and displayed as "<10"
    small = df_dim[(df_dim["enrolments"] > 0) & (df_dim["enrolments"] < SMALL_CELL_THRESHOLD)]
    assert len(small) == 72
    assert small["suppressed_lt10"].all()
    assert (small["display_enrolments"] == "<10").all()


def test_gold_csv_contracts(repo_root: Path) -> None:
    df_inst = pd.read_csv(repo_root / "outputs" / "kpis" / "institution_access_kpis_by_year.csv")
    assert len(df_inst) == len(INSTITUTION_SECTOR_MAP) * len(ACADEMIC_YEARS) == 182
    assert set(df_inst["academic_year"].unique()) == set(ACADEMIC_YEARS)
    assert set(df_inst["institute"].unique()) == set(INSTITUTION_SECTOR_MAP.keys())

    df_cty = pd.read_csv(repo_root / "outputs" / "geography" / "county_deprivation_enrolments.csv")
    assert len(df_cty) == 26
    assert int(round(df_cty["pop_2022"].sum())) == 5149139
    assert int(df_cty["n_electoral_divisions"].sum()) == 3417

    df_dict = pd.read_csv(repo_root / "outputs" / "kpis" / "kpi_dictionary.csv")
    assert len(df_dict) == 6
    df_rag = pd.read_csv(repo_root / "outputs" / "kpis" / "nap_rag_monitoring.csv")
    assert len(df_rag) == 29
    assert len(df_rag[df_rag["entity_type"] == "Institution"]) == 26


def test_duckdb_warehouse_layers_if_present() -> None:
    if not DB_PATH.exists():
        # In the clean GitHub release copy, warehouse/accesslens.duckdb is intentionally excluded
        return
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        n_ed = con.execute("SELECT COUNT(*) FROM bronze.pobal_ed_2022").fetchone()[0]
        assert n_ed == 3417
        n_quar_sum = con.execute("SELECT COUNT(*) FROM silver.quarantine_summary_rows").fetchone()[0]
        assert n_quar_sum == 6058
        n_quar_cty = con.execute("SELECT COUNT(*) FROM silver.quarantine_unmapped_county").fetchone()[0]
        assert n_quar_cty == 14
        n_gold_inst = con.execute("SELECT COUNT(*) FROM gold.fact_institution_year").fetchone()[0]
        assert n_gold_inst == 182
    finally:
        con.close()
