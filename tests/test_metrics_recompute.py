"""Step 7 Tests: Metric recomputation from DuckDB and Gold CSV outputs against audit.json."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Dict

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from accesslens.config import DB_PATH


def test_recompute_maynooth_and_sector_metrics_from_csv_and_duckdb(
    repo_root: Path, audit_payload: Dict
) -> None:
    metrics = audit_payload["metrics"]
    df_inst = pd.read_csv(repo_root / "outputs" / "kpis" / "institution_access_kpis_by_year.csv")

    mu_19 = df_inst[
        (df_inst["institute"] == "Maynooth University")
        & (df_inst["academic_year"] == "2019/2020")
    ].iloc[0]
    mu_24 = df_inst[
        (df_inst["institute"] == "Maynooth University")
        & (df_inst["academic_year"] == "2024/2025")
    ].iloc[0]
    mu_25 = df_inst[
        (df_inst["institute"] == "Maynooth University")
        & (df_inst["academic_year"] == "2025/2026")
    ].iloc[0]

    assert int(mu_19["total_enrolments"]) == metrics["mu_enrol_2019_20"]["value"] == 13005
    assert int(mu_24["total_enrolments"]) == metrics["mu_enrol_2024_25"]["value"] == 15560
    assert int(mu_25["total_enrolments"]) == metrics["mu_enrol_2025_26"]["value"] == 15945
    assert (
        int(mu_25["total_enrolments"] - mu_19["total_enrolments"])
        == metrics["mu_enrol_6yr_added"]["value"]
        == 2940
    )

    recomp_growth = (mu_25["total_enrolments"] - mu_19["total_enrolments"]) / mu_19[
        "total_enrolments"
    ]
    assert math.isclose(recomp_growth, metrics["mu_enrol_6yr_growth"]["value"], rel_tol=1e-9)

    assert int(mu_25["mature_24plus_enrolments"]) == metrics["mu_mature_2025_26"]["value"] == 3140
    recomp_mat_share = mu_25["mature_24plus_enrolments"] / mu_25["total_enrolments"]
    assert math.isclose(recomp_mat_share, metrics["mu_mature_share_2025_26"]["value"], rel_tol=1e-9)

    assert int(mu_25["flexible_enrolments"]) == metrics["mu_pt_2025_26"]["value"] == 1665
    assert int(mu_25["ug_access_pathway_enrolments"]) == metrics["mu_ug_pathway_2025_26"]["value"] == 880
    assert int(mu_25["honours_degree_enrolments"]) == metrics["mu_hons_2025_26"]["value"] == 12430

    # Sector totals
    sec_25 = df_inst[df_inst["academic_year"] == "2025/2026"]
    assert int(sec_25["total_enrolments"].sum()) == metrics["sector_enrol_2025_26"]["value"] == 283940
    assert int(sec_25["foundation_access_enrolments"].sum()) == metrics["sector_fa_2025_26"]["value"] == 1035

    # If DuckDB is present locally, verify Gold SQL query matches audit.json directly
    if DB_PATH.exists():
        con = duckdb.connect(str(DB_PATH), read_only=True)
        try:
            mu_sql = con.execute(
                """
                SELECT total_enrolments, mature_24plus_enrolments, part_time_enrolments, honours_degree_enrolments
                FROM gold.fact_institution_year
                WHERE institute = 'Maynooth University' AND academic_year = '2025/2026'
                """
            ).fetchone()
            assert mu_sql == (15945, 3140, 1665, 12430)
        finally:
            con.close()


def test_recompute_county_deprivation_correlations(
    repo_root: Path, audit_payload: Dict
) -> None:
    metrics = audit_payload["metrics"]
    df_cty = pd.read_csv(repo_root / "outputs" / "geography" / "county_deprivation_enrolments.csv")
    assert len(df_cty) == 26

    x = df_cty["pop_wt_rel_deprivation"].to_numpy(dtype=float)
    y = df_cty["enrol_per_1k_pop_2025_2026"].to_numpy(dtype=float)

    r_res = stats.pearsonr(x, y)
    rho_res = stats.spearmanr(x, y)

    assert math.isclose(float(r_res.statistic), metrics["corr_rel_2025_26_r"]["value"], rel_tol=1e-9)
    assert math.isclose(float(r_res.pvalue), metrics["corr_rel_2025_26_p"]["value"], rel_tol=1e-9)
    assert math.isclose(float(rho_res.statistic), metrics["corr_rel_2025_26_rho"]["value"], rel_tol=1e-9)

    # Verify Maynooth deprived-county catchment share
    dep_rows = df_cty[df_cty["pop_wt_rel_deprivation"] < 0]
    assert len(dep_rows) == metrics["n_deprived_counties"]["value"] == 19
    mu_dep = int(dep_rows["mu_enrol_2025_2026"].sum())
    mu_tot_cty = int(df_cty["mu_enrol_2025_2026"].sum())
    assert mu_dep == metrics["mu_deprived_county_enrol_2025_26"]["value"] == 4775
    assert mu_tot_cty == metrics["mu_county_mapped_2025_26"]["value"] == 14720
    assert math.isclose(
        mu_dep / mu_tot_cty,
        metrics["mu_deprived_county_share_2025_26"]["value"],
        rel_tol=1e-9,
    )
