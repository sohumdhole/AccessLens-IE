"""Step 2: Access indicators by year and institution (Foundation and Access enrolments,
mature students 24+, part-time and flexible study, field of study mix, and Maynooth University
benchmarked against the university sector average and peers with year-on-year change).
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from .audit import Audit
from .config import (
    ACADEMIC_YEARS,
    FOCUS_INSTITUTION,
    IUA_UNIVERSITIES,
    OUT,
    SMALL_CELL_THRESHOLD,
    WAREHOUSE,
)


def _suppress_str(val: int) -> str:
    if 0 < val < SMALL_CELL_THRESHOLD:
        return "<10"
    return str(int(val))


def run() -> dict:
    a = Audit("step2_access_indicators")
    con = duckdb.connect(str(WAREHOUSE), read_only=True)

    fact_iy = con.execute("SELECT * FROM gold.fact_institution_year ORDER BY institute, academic_year").df()
    fact_dim = con.execute("SELECT * FROM gold.fact_institution_dimension_year").df()
    fact_cty_inst = con.execute("SELECT * FROM gold.fact_county_institution_year").df()
    fact_cty_dep = con.execute("SELECT * FROM gold.fact_county_deprivation").df()
    con.close()

    kpi_dir = OUT / "kpis"
    kpi_dir.mkdir(parents=True, exist_ok=True)

    # 1. Compute deprived-county Irish-domiciled student share for each institution x year
    deprived_counties = set(
        fact_cty_dep[fact_cty_dep["pop_wt_rel_deprivation"] < 0.0]["county"]
    )
    cty_flow = fact_cty_inst.copy()
    cty_flow["is_deprived_county"] = cty_flow["county"].isin(deprived_counties)
    inst_cty_agg = (
        cty_flow.groupby(["institute", "academic_year"])
        .agg(
            irish_county_mapped_enrolments=("enrolments", "sum"),
            deprived_county_enrolments=(
                "enrolments",
                lambda s: int(s[cty_flow.loc[s.index, "is_deprived_county"]].sum()),
            ),
        )
        .reset_index()
    )
    inst_cty_agg["deprived_county_share"] = np.where(
        inst_cty_agg["irish_county_mapped_enrolments"] > 0,
        inst_cty_agg["deprived_county_enrolments"]
        / inst_cty_agg["irish_county_mapped_enrolments"],
        np.nan,
    )

    panel = fact_iy.merge(inst_cty_agg, on=["institute", "academic_year"], how="left")
    panel["irish_county_mapped_enrolments"] = panel["irish_county_mapped_enrolments"].fillna(0).astype(int)
    panel["deprived_county_enrolments"] = panel["deprived_county_enrolments"].fillna(0).astype(int)
    panel["foundation_access_display"] = panel["foundation_access_enrolments"].apply(
        _suppress_str
    )

    export_cols = [
        "academic_year",
        "institute",
        "combined_institute",
        "sector_group",
        "is_iua_university",
        "in_hea_scope",
        "total_enrolments",
        "yoy_enrolment_change",
        "foundation_access_enrolments",
        "foundation_access_display",
        "foundation_access_share",
        "ug_access_pathway_enrolments",
        "ug_access_pathway_share_of_total",
        "ug_access_pathway_share_of_ug",
        "honours_degree_enrolments",
        "mature_24plus_enrolments",
        "mature_24plus_share",
        "young_23under_enrolments",
        "part_time_enrolments",
        "other_mode_enrolments",
        "flexible_enrolments",
        "part_time_share",
        "flexible_share",
        "undergraduate_enrolments",
        "postgraduate_enrolments",
        "undergraduate_share",
        "education_enrolments",
        "social_sciences_enrolments",
        "edu_soc_enrolments",
        "edu_soc_share",
        "irish_county_mapped_enrolments",
        "deprived_county_enrolments",
        "deprived_county_share",
    ]
    panel_out = panel[export_cols].sort_values(["academic_year", "institute"]).reset_index(drop=True)
    panel_out.to_csv(kpi_dir / "institution_access_kpis_by_year.csv", index=False)

    # 2. Benchmark time series (2019/2020 to 2025/2026):
    #    - Maynooth University
    #    - Traditional Universities (7 IUA universities pooled & peer mean)
    #    - Technological Universities / IoTs (pooled)
    #    - All HEA-Funded Institutions (pooled sector total)
    bench_rows = []
    for yr in ACADEMIC_YEARS:
        sub_yr = panel[panel["academic_year"] == yr]
        groups = [
            ("Maynooth University", sub_yr[sub_yr["institute"] == FOCUS_INSTITUTION]),
            ("Traditional Universities (7 IUA)", sub_yr[sub_yr["is_iua_university"]]),
            (
                "Traditional Universities Excl. Maynooth (6 Peers)",
                sub_yr[sub_yr["is_iua_university"] & (sub_yr["institute"] != FOCUS_INSTITUTION)],
            ),
            (
                "Technological Universities / IoTs",
                sub_yr[sub_yr["sector_group"] == "Technological University / IoT"],
            ),
            ("All HEA Institutions (Sector)", sub_yr[sub_yr["in_hea_scope"]]),
        ]
        for gname, gdf in groups:
            tot = int(gdf["total_enrolments"].sum())
            ug = int(gdf["undergraduate_enrolments"].sum())
            pg = int(gdf["postgraduate_enrolments"].sum())
            fa = int(gdf["foundation_access_enrolments"].sum())
            ug_path = int(gdf["ug_access_pathway_enrolments"].sum())
            hons = int(gdf["honours_degree_enrolments"].sum())
            mat = int(gdf["mature_24plus_enrolments"].sum())
            yng = int(gdf["young_23under_enrolments"].sum())
            pt = int(gdf["part_time_enrolments"].sum())
            oth = int(gdf["other_mode_enrolments"].sum())
            flx = int(gdf["flexible_enrolments"].sum())
            ed_soc = int(gdf["edu_soc_enrolments"].sum())
            ir_map = int(gdf["irish_county_mapped_enrolments"].sum())
            dep_cty = int(gdf["deprived_county_enrolments"].sum())
            bench_rows.append(
                {
                    "academic_year": yr,
                    "benchmark_group": gname,
                    "n_institutions": int(len(gdf)),
                    "total_enrolments": tot,
                    "undergraduate_enrolments": ug,
                    "postgraduate_enrolments": pg,
                    "foundation_access_enrolments": fa,
                    "foundation_access_share": fa / tot if tot else np.nan,
                    "ug_access_pathway_enrolments": ug_path,
                    "ug_access_pathway_share_of_total": ug_path / tot if tot else np.nan,
                    "ug_access_pathway_share_of_ug": ug_path / ug if ug else np.nan,
                    "honours_degree_enrolments": hons,
                    "honours_degree_share": hons / tot if tot else np.nan,
                    "mature_24plus_enrolments": mat,
                    "mature_24plus_share": mat / tot if tot else np.nan,
                    "young_23under_enrolments": yng,
                    "part_time_enrolments": pt,
                    "other_mode_enrolments": oth,
                    "flexible_enrolments": flx,
                    "part_time_share": pt / tot if tot else np.nan,
                    "flexible_share": flx / tot if tot else np.nan,
                    "undergraduate_share": ug / tot if tot else np.nan,
                    "edu_soc_enrolments": ed_soc,
                    "edu_soc_share": ed_soc / tot if tot else np.nan,
                    "irish_county_mapped_enrolments": ir_map,
                    "deprived_county_enrolments": dep_cty,
                    "deprived_county_share": dep_cty / ir_map if ir_map else np.nan,
                }
            )
    df_bench = pd.DataFrame(bench_rows)
    df_bench["prev_total"] = df_bench.groupby("benchmark_group")["total_enrolments"].shift(1)
    df_bench["yoy_enrolment_change"] = (
        df_bench["total_enrolments"] - df_bench["prev_total"]
    ) / df_bench["prev_total"]
    base_totals = (
        df_bench[df_bench["academic_year"] == "2019/2020"]
        .set_index("benchmark_group")["total_enrolments"]
        .to_dict()
    )
    df_bench["index_2019_20_eq_100"] = df_bench.apply(
        lambda r: (r["total_enrolments"] / base_totals[r["benchmark_group"]]) * 100.0,
        axis=1,
    )
    df_bench.drop(columns=["prev_total"]).to_csv(
        kpi_dir / "maynooth_vs_benchmarks_by_year.csv", index=False
    )

    # 3. 2025/2026 University Peer Scorecard (with 6-year and YoY deltas)
    p19 = panel[panel["academic_year"] == "2019/2020"].set_index("institute")
    p24 = panel[panel["academic_year"] == "2024/2025"].set_index("institute")
    p25 = panel[panel["academic_year"] == "2025/2026"].set_index("institute")

    peer_rows = []
    for inst in IUA_UNIVERSITIES:
        r19, r24, r25 = p19.loc[inst], p24.loc[inst], p25.loc[inst]
        peer_rows.append(
            {
                "institute": inst,
                "enrolments_2019_20": int(r19["total_enrolments"]),
                "enrolments_2024_25": int(r24["total_enrolments"]),
                "enrolments_2025_26": int(r25["total_enrolments"]),
                "growth_6yr_pct": (r25["total_enrolments"] - r19["total_enrolments"])
                / r19["total_enrolments"],
                "growth_yoy_pct": (r25["total_enrolments"] - r24["total_enrolments"])
                / r24["total_enrolments"],
                "foundation_access_2025_26": int(r25["foundation_access_enrolments"]),
                "ug_access_pathway_2025_26": int(r25["ug_access_pathway_enrolments"]),
                "ug_access_pathway_share_ug_2025_26": float(
                    r25["ug_access_pathway_share_of_ug"]
                ),
                "mature_24plus_2025_26": int(r25["mature_24plus_enrolments"]),
                "mature_share_2019_20": float(r19["mature_24plus_share"]),
                "mature_share_2025_26": float(r25["mature_24plus_share"]),
                "mature_share_6yr_change_pp": float(
                    r25["mature_24plus_share"] - r19["mature_24plus_share"]
                ),
                "flexible_2025_26": int(r25["flexible_enrolments"]),
                "part_time_share_2025_26": float(r25["part_time_share"]),
                "flexible_share_2025_26": float(r25["flexible_share"]),
                "edu_soc_share_2025_26": float(r25["edu_soc_share"]),
                "deprived_county_enrolments_2025_26": int(
                    r25["deprived_county_enrolments"]
                ),
                "deprived_county_share_2025_26": float(r25["deprived_county_share"]),
            }
        )
    df_peers = pd.DataFrame(peer_rows).sort_values(
        "enrolments_2025_26", ascending=False
    )
    df_peers.to_csv(kpi_dir / "university_peer_scorecard_2025_26.csv", index=False)

    # 4. Field of Study mix comparison (2019/2020 vs 2025/2026)
    fs_dim = fact_dim[fact_dim["dimension_type"] == "Field of Study"].copy()
    fs_rows = []
    for yr in ["2019/2020", "2024/2025", "2025/2026"]:
        sub = fs_dim[fs_dim["academic_year"] == yr]
        mu_sub = sub[sub["institute"] == FOCUS_INSTITUTION].set_index("category")[
            "enrolments"
        ]
        iua_sub = (
            sub[sub["institute"].isin(IUA_UNIVERSITIES)]
            .groupby("category")["enrolments"]
            .sum()
        )
        sec_sub = sub.groupby("category")["enrolments"].sum()
        mu_tot = float(mu_sub.sum())
        iua_tot = float(iua_sub.sum())
        sec_tot = float(sec_sub.sum())
        for cat in sorted(sec_sub.index):
            m_v = int(mu_sub.get(cat, 0))
            u_v = int(iua_sub.get(cat, 0))
            s_v = int(sec_sub.get(cat, 0))
            fs_rows.append(
                {
                    "academic_year": yr,
                    "field_of_study": cat,
                    "maynooth_enrolments": m_v,
                    "maynooth_display": _suppress_str(m_v),
                    "maynooth_share": m_v / mu_tot,
                    "iua_universities_enrolments": u_v,
                    "iua_universities_share": u_v / iua_tot,
                    "hea_sector_enrolments": s_v,
                    "hea_sector_share": s_v / sec_tot,
                    "maynooth_vs_sector_diff_pp": (m_v / mu_tot) - (s_v / sec_tot),
                }
            )
    df_fs = pd.DataFrame(fs_rows)
    df_fs.to_csv(kpi_dir / "field_of_study_mix_comparison.csv", index=False)

    # 5. Programme Type profile (2019/2020 vs 2025/2026)
    pt_dim = fact_dim[fact_dim["dimension_type"] == "Programme Type"].copy()
    pt_rows = []
    for yr in ["2019/2020", "2024/2025", "2025/2026"]:
        sub = pt_dim[pt_dim["academic_year"] == yr]
        mu_sub = sub[sub["institute"] == FOCUS_INSTITUTION].set_index("category")[
            "enrolments"
        ]
        iua_sub = (
            sub[sub["institute"].isin(IUA_UNIVERSITIES)]
            .groupby("category")["enrolments"]
            .sum()
        )
        sec_sub = sub.groupby("category")["enrolments"].sum()
        mu_tot = float(mu_sub.sum())
        iua_tot = float(iua_sub.sum())
        sec_tot = float(sec_sub.sum())
        for cat in sorted(sec_sub.index):
            m_v = int(mu_sub.get(cat, 0))
            u_v = int(iua_sub.get(cat, 0))
            s_v = int(sec_sub.get(cat, 0))
            pt_rows.append(
                {
                    "academic_year": yr,
                    "programme_type": cat,
                    "maynooth_enrolments": m_v,
                    "maynooth_display": _suppress_str(m_v),
                    "maynooth_share": m_v / mu_tot,
                    "iua_universities_enrolments": u_v,
                    "iua_universities_share": u_v / iua_tot,
                    "hea_sector_enrolments": s_v,
                    "hea_sector_share": s_v / sec_tot,
                }
            )
    df_pt = pd.DataFrame(pt_rows)
    df_pt.to_csv(kpi_dir / "programme_type_profile_2025_26.csv", index=False)

    # -------------------------------------------------------------------------
    # RECORD AUDIT METRICS FOR STEP 2
    # -------------------------------------------------------------------------
    b_idx = df_bench.set_index(["benchmark_group", "academic_year"])
    mu_19 = b_idx.loc[("Maynooth University", "2019/2020")]
    mu_24 = b_idx.loc[("Maynooth University", "2024/2025")]
    mu_25 = b_idx.loc[("Maynooth University", "2025/2026")]
    iua_19 = b_idx.loc[("Traditional Universities (7 IUA)", "2019/2020")]
    iua_25 = b_idx.loc[("Traditional Universities (7 IUA)", "2025/2026")]
    sec_19 = b_idx.loc[("All HEA Institutions (Sector)", "2019/2020")]
    sec_24 = b_idx.loc[("All HEA Institutions (Sector)", "2024/2025")]
    sec_25 = b_idx.loc[("All HEA Institutions (Sector)", "2025/2026")]

    # Headline totals & growth
    a.put("mu_enrol_2019_20", int(mu_19["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_enrol_2024_25", int(mu_24["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_enrol_2025_26", int(mu_25["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_enrol_6yr_added", int(mu_25["total_enrolments"] - mu_19["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_enrol_6yr_growth", float((mu_25["total_enrolments"] - mu_19["total_enrolments"]) / mu_19["total_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_enrol_yoy_growth", float(mu_25["yoy_enrolment_change"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    a.put("iua_enrol_2019_20", int(iua_19["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("iua_enrol_2025_26", int(iua_25["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("iua_enrol_6yr_growth", float((iua_25["total_enrolments"] - iua_19["total_enrolments"]) / iua_19["total_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    a.put("sector_enrol_2019_20", int(sec_19["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_enrol_2024_25", int(sec_24["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_enrol_2025_26", int(sec_25["total_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_enrol_6yr_growth", float((sec_25["total_enrolments"] - sec_19["total_enrolments"]) / sec_19["total_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_enrol_yoy_growth", float(sec_25["yoy_enrolment_change"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    # Undergraduate vs Postgraduate
    a.put("mu_ug_2025_26", int(mu_25["undergraduate_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_pg_2025_26", int(mu_25["postgraduate_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_ug_share_2025_26", float(mu_25["undergraduate_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_ug_2025_26", int(sec_25["undergraduate_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_pg_2025_26", int(sec_25["postgraduate_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_ug_share_2025_26", float(sec_25["undergraduate_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    # Foundation & Access and broader non-degree UG pathways
    a.put("sector_fa_2019_20", int(sec_19["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_fa_2024_25", int(sec_24["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_fa_2025_26", int(sec_25["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_fa_6yr_growth", float((sec_25["foundation_access_enrolments"] - sec_19["foundation_access_enrolments"]) / sec_19["foundation_access_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_fa_2019_20", int(mu_19["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_fa_2024_25", int(mu_24["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_fa_2025_26", int(mu_25["foundation_access_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_ug_pathway_2025_26", int(mu_25["ug_access_pathway_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_ug_pathway_share_tot_2025_26", float(mu_25["ug_access_pathway_share_of_total"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_ug_pathway_share_ug_2025_26", float(mu_25["ug_access_pathway_share_of_ug"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("iua_ug_pathway_share_ug_2025_26", float(iua_25["ug_access_pathway_share_of_ug"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_ug_pathway_share_ug_2025_26", float(sec_25["ug_access_pathway_share_of_ug"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_hons_2019_20", int(mu_19["honours_degree_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_hons_2025_26", int(mu_25["honours_degree_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_hons_6yr_growth", float((mu_25["honours_degree_enrolments"] - mu_19["honours_degree_enrolments"]) / mu_19["honours_degree_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_hons_share_2025_26", float(mu_25["honours_degree_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_hons_share_2025_26", float(sec_25["honours_degree_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    # Top Foundation and Access providers in 2025/2026
    fa_25 = p25["foundation_access_enrolments"]
    a.put("fa_atu_donegal_2025_26", int(fa_25.loc["ATU Donegal"]), "int", "institution_access_kpis_by_year.csv")
    a.put("fa_tud_city_2025_26", int(fa_25.loc["TU Dublin City"]), "int", "institution_access_kpis_by_year.csv")
    a.put("fa_tcd_2025_26", int(fa_25.loc["Trinity College Dublin"]), "int", "institution_access_kpis_by_year.csv")
    a.put("fa_uog_2025_26", int(fa_25.loc["University of Galway"]), "int", "institution_access_kpis_by_year.csv")
    a.put("fa_mtu_kerry_2025_26", int(fa_25.loc["MTU Kerry"]), "int", "institution_access_kpis_by_year.csv")

    # Mature students (24+ age group)
    a.put("mu_mature_2019_20", int(mu_19["mature_24plus_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_2024_25", int(mu_24["mature_24plus_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_2025_26", int(mu_25["mature_24plus_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_share_2019_20", float(mu_19["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_share_2024_25", float(mu_24["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_share_2025_26", float(mu_25["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_mature_share_6yr_pp", float(mu_25["mature_24plus_share"] - mu_19["mature_24plus_share"]), "signed_pp", "maynooth_vs_benchmarks_by_year.csv")
    a.put("iua_mature_share_2025_26", float(iua_25["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_mature_2025_26", int(sec_25["mature_24plus_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_mature_share_2019_20", float(sec_19["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_mature_share_2025_26", float(sec_25["mature_24plus_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_young_2019_20", int(mu_19["young_23under_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_young_2025_26", int(mu_25["young_23under_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_young_6yr_growth", float((mu_25["young_23under_enrolments"] - mu_19["young_23under_enrolments"]) / mu_19["young_23under_enrolments"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    # Part-time and flexible modes of study
    a.put("mu_pt_2019_20", int(mu_19["part_time_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_pt_2024_25", int(mu_24["part_time_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_pt_2025_26", int(mu_25["part_time_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_flex_share_2019_20", float(mu_19["flexible_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_flex_share_2024_25", float(mu_24["flexible_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_flex_share_2025_26", float(mu_25["flexible_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("iua_flex_share_2025_26", float(iua_25["flexible_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_pt_2025_26", int(sec_25["part_time_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_other_mode_2025_26", int(sec_25["other_mode_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_flex_2025_26", int(sec_25["flexible_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_pt_share_2025_26", float(sec_25["part_time_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_flex_share_2025_26", float(sec_25["flexible_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")

    # Field of Study mix highlights (2025/2026)
    fs_25 = df_fs[df_fs["academic_year"] == "2025/2026"].set_index("field_of_study")
    fs_19 = df_fs[df_fs["academic_year"] == "2019/2020"].set_index("field_of_study")
    a.put("mu_fs_bus_2025_26", int(fs_25.loc["Business, administration and law", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_bus_share_2025_26", float(fs_25.loc["Business, administration and law", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_bus_share_2025_26", float(fs_25.loc["Business, administration and law", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_arts_2025_26", int(fs_25.loc["Arts and humanities", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_arts_share_2025_26", float(fs_25.loc["Arts and humanities", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_arts_share_2025_26", float(fs_25.loc["Arts and humanities", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_natsci_2025_26", int(fs_25.loc["Natural sciences, mathematics and statistics", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_natsci_share_2025_26", float(fs_25.loc["Natural sciences, mathematics and statistics", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_natsci_share_2025_26", float(fs_25.loc["Natural sciences, mathematics and statistics", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_soc_2025_26", int(fs_25.loc["Social sciences, journalism and information", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_soc_share_2025_26", float(fs_25.loc["Social sciences, journalism and information", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_soc_share_2025_26", float(fs_25.loc["Social sciences, journalism and information", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_edu_2025_26", int(fs_25.loc["Education", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_edu_share_2025_26", float(fs_25.loc["Education", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_edu_share_2025_26", float(fs_25.loc["Education", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_edusoc_2025_26", int(mu_25["edu_soc_enrolments"]), "int", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_fs_edusoc_share_2025_26", float(mu_25["edu_soc_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("sector_fs_edusoc_share_2025_26", float(sec_25["edu_soc_share"]), "pct", "maynooth_vs_benchmarks_by_year.csv")
    a.put("mu_fs_health_2019_20", int(fs_19.loc["Health and welfare", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_health_2025_26", int(fs_25.loc["Health and welfare", "maynooth_enrolments"]), "int", "field_of_study_mix_comparison.csv")
    a.put("mu_fs_health_share_2025_26", float(fs_25.loc["Health and welfare", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_health_share_2025_26", float(fs_25.loc["Health and welfare", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put(
        "mu_fs_health_6yr_growth",
        float(
            (
                fs_25.loc["Health and welfare", "maynooth_enrolments"]
                - fs_19.loc["Health and welfare", "maynooth_enrolments"]
            )
            / fs_19.loc["Health and welfare", "maynooth_enrolments"]
        ),
        "pct",
        "field_of_study_mix_comparison.csv",
    )
    a.put("mu_fs_eng_share_2025_26", float(fs_25.loc["Engineering, manufacturing and construction", "maynooth_share"]), "pct", "field_of_study_mix_comparison.csv")
    a.put("sector_fs_eng_share_2025_26", float(fs_25.loc["Engineering, manufacturing and construction", "hea_sector_share"]), "pct", "field_of_study_mix_comparison.csv")

    a.save(
        [
            "outputs/kpis/institution_access_kpis_by_year.csv",
            "outputs/kpis/maynooth_vs_benchmarks_by_year.csv",
            "outputs/kpis/university_peer_scorecard_2025_26.csv",
            "outputs/kpis/field_of_study_mix_comparison.csv",
            "outputs/kpis/programme_type_profile_2025_26.csv",
        ]
    )
    return {
        "panel": panel_out,
        "benchmarks": df_bench,
        "peers": df_peers,
        "field_mix": df_fs,
        "programme_profile": df_pt,
    }
