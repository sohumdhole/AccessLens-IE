"""Step 4: KPI framework mapped to National Access Plan 2022-2028 goals
(KPI dictionary with definition, source, grain, NAP goal; RAG-style monitoring view with stated thresholds).
"""
from __future__ import annotations

import pandas as pd

from .audit import Audit
from .config import (
    FOCUS_INSTITUTION,
    IUA_UNIVERSITIES,
    NAP_2022_2028_TARGETS,
    OUT,
    RAG_THRESHOLDS,
)


def _rag_status(val: float, key: str) -> str:
    if pd.isna(val):
        return "NOT SCORED"
    th = RAG_THRESHOLDS[key]
    if val >= th["green"]:
        return "GREEN"
    if val >= th["amber"]:
        return "AMBER"
    return "RED"


def run() -> dict:
    a = Audit("step4_kpi_framework")
    kpi_dir = OUT / "kpis"
    kpi_dir.mkdir(parents=True, exist_ok=True)

    # 1. KPI Dictionary mapped to National Access Plan 2022-2028 goals
    kpi_dict_rows = [
        {
            "kpi_code": "KPI_01_MATURE_SHARE",
            "kpi_name": "Mature Student Participation Share (Age 24+)",
            "definition": "Proportion of total enrolled students aged 24 years and over on 1 January of the academic year.",
            "formula": "Enrolments(Age Group = '24+') / Total Enrolments",
            "source_dataset": "HEA SRS Access our Data (Institute x Age Group, 2019/2020 to 2025/2026)",
            "reporting_grain": "Institution x Academic Year (all course levels)",
            "nap_2022_2028_goal": "NAP Goal 1 (Inflow & Widening Participation) & Priority Group: Mature Students",
            "nap_official_target": "Raise mature entrants from socio-economically disadvantaged areas from 11% to 20% of new entrants by 2028",
            "analytical_rag_thresholds": "GREEN >= 25.0%; AMBER 18.0% to <25.0%; RED < 18.0% (all-level headcount proxy)",
            "honest_scope_note": "Public SRS export measures all-level age 24+ headcount rather than undergraduate new entrants aged 23+ on entry from disadvantaged areas.",
        },
        {
            "kpi_code": "KPI_02_FLEXIBLE_SHARE",
            "kpi_name": "Part-Time and Flexible Study Share",
            "definition": "Proportion of enrolled students studying via Part-Time or Other flexible/remote modes rather than Full-Time.",
            "formula": "(Enrolments(Mode = 'Part-time') + Enrolments(Mode = 'Other')) / Total Enrolments",
            "source_dataset": "HEA SRS Access our Data (Institute x Mode of Study, 2019/2020 to 2025/2026)",
            "reporting_grain": "Institution x Academic Year",
            "nap_2022_2028_goal": "NAP Goal 2 (Flexibility & Inclusivity) - flexible, part-time, and lifelong learning provision",
            "nap_official_target": "Expand flexible and part-time pathways across HEIs to support working, lone-parent, and mature learners",
            "analytical_rag_thresholds": "GREEN >= 15.0%; AMBER 10.0% to <15.0%; RED < 10.0%",
            "honest_scope_note": "Public SRS categorises modes into Full-time, Part-time, and Other (remote/blended/modular).",
        },
        {
            "kpi_code": "KPI_03_UG_PATHWAY_BREADTH",
            "kpi_name": "Undergraduate Access and Non-Honours Pathway Breadth",
            "definition": "Share of undergraduate enrolments in Foundation and Access courses, Certificates, Higher Certificates, Ordinary Degrees, and UG Diplomas/Occasionals.",
            "formula": "Enrolments(Foundation & Access + Certs + Higher Certs + Ord Degrees + UG Diplomas/Occasionals) / Undergraduate Enrolments",
            "source_dataset": "HEA SRS Access our Data (Institute x Programme Type & Course Level, 2019/2020 to 2025/2026)",
            "reporting_grain": "Institution x Academic Year",
            "nap_2022_2028_goal": "NAP Goal 1 (Pathways into Higher Education) - Foundation, QQI/FET progression, and sub-degree entry routes",
            "nap_official_target": "No numeric NAP target is used for this proxy; it tracks sub-degree and foundation entry routes into higher education",
            "analytical_rag_thresholds": "GREEN >= 8.0%; AMBER 5.0% to <8.0%; RED < 5.0% of Undergraduate Enrolments",
            "honest_scope_note": "Direct HEAR, DARE, and QQI/FET entrants who enrol straight into Honours Degrees are counted under Honours Degrees in public SRS.",
        },
        {
            "kpi_code": "KPI_04_DEPRIVED_COUNTY_REACH",
            "kpi_name": "Disadvantaged-County Regional Reach (Ecological Proxy)",
            "definition": "Proportion of an institution's county-mapped Irish-domiciled students originating from the 19 Irish counties with below-average Pobal HP 2022 relative affluence (population-weighted score < 0).",
            "formula": "Irish-Domiciled Enrolments from Counties with Pobal Score < 0 / Total County-Mapped Irish-Domiciled Enrolments",
            "source_dataset": "HEA SRS (County x Institute, Irish domiciled) joined with Pobal HP Deprivation Index 2022 (ED level, CC BY 4.0)",
            "reporting_grain": "Institution x Academic Year (ecological county-origin grain)",
            "nap_2022_2028_goal": "NAP Goal 1 (Socio-Economic Disadvantage) - raise transition rate from disadvantaged areas from 42% to 54%",
            "nap_official_target": "Raise higher education transition rate from disadvantaged areas from 42% baseline to 54% by 2028",
            "analytical_rag_thresholds": "GREEN >= 20.0%; AMBER 14.0% to <20.0%; RED < 14.0%",
            "honest_scope_note": "Ecological proxy at county level (26 counties). Does not measure individual student household deprivation or Small Area DIS.",
        },
        {
            "kpi_code": "KPI_05_EDU_SOC_SHARE",
            "kpi_name": "Education and Social Sciences Field Share (Context Indicator, Not RAG-Scored)",
            "definition": "Proportion of total enrolments in Education and Social sciences, journalism and information (key diversity-in-professions and community leadership disciplines).",
            "formula": "(Enrolments(Field = 'Education') + Enrolments(Field = 'Social sciences, journalism and information')) / Total Enrolments",
            "source_dataset": "HEA SRS Access our Data (Institute x Field of Study, 2019/2020 to 2025/2026)",
            "reporting_grain": "Institution x Academic Year",
            "nap_2022_2028_goal": "Context only: describes institutional discipline mix, not a widening participation measure",
            "nap_official_target": "None (context indicator)",
            "analytical_rag_thresholds": "Not RAG-scored (context indicator)",
            "honest_scope_note": "Discipline mix reflects institutional mission, not access or equity outcomes, so it is excluded from RAG scoring.",
        },
        {
            "kpi_code": "KPI_06_DISABILITY_PARTICIPATION_GAP",
            "kpi_name": "Students with Disabilities New Entrant Share (Data Gap Indicator)",
            "definition": "Share of new entrants disclosing a disability supported via the Fund for Students with Disabilities / DARE.",
            "formula": "New Entrants with Disability / Total New Entrants (Not available in public HEA SRS interactive download)",
            "source_dataset": "HEA Equal Access Survey / Institutional MAP & Disability Office Records (Not in public SRS Shiny export)",
            "reporting_grain": "Institution x Academic Year (Reported separately in HEA Equal Access publications)",
            "nap_2022_2028_goal": "NAP Priority Group: Students with Disabilities (including autistic students and students with intellectual disabilities)",
            "nap_official_target": "Increase new entrants with a disability from 12.4% to 16% of new entrants by 2028",
            "analytical_rag_thresholds": "DATA GAP IN PUBLIC SRS (Tracked internally by MAP / Disability Office)",
            "honest_scope_note": "Public HEA 'Access our Data - Students' portal does not include per-student disability or Equal Access Survey indicators.",
        },
    ]
    df_dict = pd.DataFrame(kpi_dict_rows)
    df_dict.to_csv(kpi_dir / "kpi_dictionary.csv", index=False)

    # 2. Build RAG monitoring view for 2025/2026 across all 26 institutions + benchmarks
    panel = pd.read_csv(kpi_dir / "institution_access_kpis_by_year.csv")
    bench = pd.read_csv(kpi_dir / "maynooth_vs_benchmarks_by_year.csv")

    p25 = panel[panel["academic_year"] == "2025/2026"].copy()
    rag_rows = []
    for _, r in p25.iterrows():
        s_mat = _rag_status(r["mature_24plus_share"], "mature_share")
        s_flx = _rag_status(r["flexible_share"], "flexible_share")
        s_pth = _rag_status(r["ug_access_pathway_share_of_ug"], "ug_access_pathway_share")
        s_dep = _rag_status(r["deprived_county_share"], "deprived_county_share")
        s_edu = "CONTEXT"  # context indicator, excluded from RAG scoring
        statuses = [s_mat, s_flx, s_pth, s_dep]
        n_green = statuses.count("GREEN")
        n_amber = statuses.count("AMBER")
        n_red = statuses.count("RED")
        if n_red >= 2:
            overall = "RED"
        elif n_green >= 3 and n_red == 0:
            overall = "GREEN"
        else:
            overall = "AMBER"

        rag_rows.append(
            {
                "entity_type": "Institution",
                "institute": r["institute"],
                "sector_group": r["sector_group"],
                "is_iua_university": bool(r["is_iua_university"]),
                "academic_year": "2025/2026",
                "total_enrolments": int(r["total_enrolments"]),
                "mature_share": float(r["mature_24plus_share"]),
                "rag_mature_share": s_mat,
                "flexible_share": float(r["flexible_share"]),
                "rag_flexible_share": s_flx,
                "ug_access_pathway_share_ug": float(r["ug_access_pathway_share_of_ug"]),
                "rag_ug_pathway_breadth": s_pth,
                "deprived_county_share": float(r["deprived_county_share"]),
                "rag_deprived_county_reach": s_dep,
                "edu_soc_share": float(r["edu_soc_share"]),
                "rag_edu_soc_share": s_edu,
                "n_green_kpis": n_green,
                "n_amber_kpis": n_amber,
                "n_red_kpis": n_red,
                "overall_rag_summary": overall,
            }
        )

    # Also add the 3 sector benchmark rows for 2025/2026
    b25 = bench[bench["academic_year"] == "2025/2026"]
    for bname in [
        "Traditional Universities (7 IUA)",
        "Technological Universities / IoTs",
        "All HEA Institutions (Sector)",
    ]:
        br = b25[b25["benchmark_group"] == bname].iloc[0]
        s_mat = _rag_status(br["mature_24plus_share"], "mature_share")
        s_flx = _rag_status(br["flexible_share"], "flexible_share")
        s_pth = _rag_status(br["ug_access_pathway_share_of_ug"], "ug_access_pathway_share")
        s_dep = _rag_status(br["deprived_county_share"], "deprived_county_share")
        s_edu = "CONTEXT"  # context indicator, excluded from RAG scoring
        statuses = [s_mat, s_flx, s_pth, s_dep]
        n_green = statuses.count("GREEN")
        n_amber = statuses.count("AMBER")
        n_red = statuses.count("RED")
        overall = "RED" if n_red >= 2 else ("GREEN" if n_green >= 3 and n_red == 0 else "AMBER")
        rag_rows.append(
            {
                "entity_type": "Sector Benchmark",
                "institute": bname,
                "sector_group": "Benchmark",
                "is_iua_university": False,
                "academic_year": "2025/2026",
                "total_enrolments": int(br["total_enrolments"]),
                "mature_share": float(br["mature_24plus_share"]),
                "rag_mature_share": s_mat,
                "flexible_share": float(br["flexible_share"]),
                "rag_flexible_share": s_flx,
                "ug_access_pathway_share_ug": float(br["ug_access_pathway_share_of_ug"]),
                "rag_ug_pathway_breadth": s_pth,
                "deprived_county_share": float(br["deprived_county_share"]),
                "rag_deprived_county_reach": s_dep,
                "edu_soc_share": float(br["edu_soc_share"]),
                "rag_edu_soc_share": s_edu,
                "n_green_kpis": n_green,
                "n_amber_kpis": n_amber,
                "n_red_kpis": n_red,
                "overall_rag_summary": overall,
            }
        )

    df_rag = pd.DataFrame(rag_rows)
    df_rag.to_csv(kpi_dir / "nap_rag_monitoring.csv", index=False)

    # -------------------------------------------------------------------------
    # RECORD AUDIT METRICS FOR STEP 4
    # -------------------------------------------------------------------------
    a.put("nap_disadv_transition_base", NAP_2022_2028_TARGETS["disadvantaged_area_transition_rate_baseline"], "pct0", "src/accesslens/config.py")
    a.put("nap_disadv_transition_target", NAP_2022_2028_TARGETS["disadvantaged_area_transition_rate_target"], "pct0", "src/accesslens/config.py")
    a.put("nap_mature_disadv_base", NAP_2022_2028_TARGETS["mature_disadvantaged_entrant_baseline"], "pct0", "src/accesslens/config.py")
    a.put("nap_mature_disadv_target", NAP_2022_2028_TARGETS["mature_disadvantaged_entrant_target"], "pct0", "src/accesslens/config.py")
    a.put("nap_disability_target", NAP_2022_2028_TARGETS["students_with_disabilities_new_entrant_target"], "pct0", "src/accesslens/config.py")
    a.put("nap_traveller_base", NAP_2022_2028_TARGETS["traveller_new_entrants_baseline"], "plain_int", "src/accesslens/config.py")
    a.put("nap_traveller_target", NAP_2022_2028_TARGETS["traveller_new_entrants_target"], "plain_int", "src/accesslens/config.py")
    a.put("nap_disability_base", NAP_2022_2028_TARGETS["students_with_disabilities_new_entrant_baseline"], "pct", "src/accesslens/config.py")

    a.put("rag_th_mature_green", RAG_THRESHOLDS["mature_share"]["green"], "pct", "src/accesslens/config.py")
    a.put("rag_th_mature_amber", RAG_THRESHOLDS["mature_share"]["amber"], "pct", "src/accesslens/config.py")
    a.put("rag_th_flex_green", RAG_THRESHOLDS["flexible_share"]["green"], "pct", "src/accesslens/config.py")
    a.put("rag_th_flex_amber", RAG_THRESHOLDS["flexible_share"]["amber"], "pct", "src/accesslens/config.py")
    a.put("rag_th_pathway_green", RAG_THRESHOLDS["ug_access_pathway_share"]["green"], "pct", "src/accesslens/config.py")
    a.put("rag_th_pathway_amber", RAG_THRESHOLDS["ug_access_pathway_share"]["amber"], "pct", "src/accesslens/config.py")
    a.put("rag_th_dep_green", RAG_THRESHOLDS["deprived_county_share"]["green"], "pct", "src/accesslens/config.py")
    a.put("rag_th_dep_amber", RAG_THRESHOLDS["deprived_county_share"]["amber"], "pct", "src/accesslens/config.py")

    mu_rag = df_rag[df_rag["institute"] == FOCUS_INSTITUTION].iloc[0]
    a.put("mu_rag_mature", mu_rag["rag_mature_share"], "str", "nap_rag_monitoring.csv")
    a.put("mu_rag_flexible", mu_rag["rag_flexible_share"], "str", "nap_rag_monitoring.csv")
    a.put("mu_rag_pathway", mu_rag["rag_ug_pathway_breadth"], "str", "nap_rag_monitoring.csv")
    a.put("mu_rag_deprived_county", mu_rag["rag_deprived_county_reach"], "str", "nap_rag_monitoring.csv")
    a.put("mu_rag_edusoc", mu_rag["rag_edu_soc_share"], "str", "nap_rag_monitoring.csv")
    a.put("mu_rag_n_green", int(mu_rag["n_green_kpis"]), "plain_int", "nap_rag_monitoring.csv")
    a.put("mu_rag_n_amber", int(mu_rag["n_amber_kpis"]), "plain_int", "nap_rag_monitoring.csv")
    a.put("mu_rag_n_red", int(mu_rag["n_red_kpis"]), "plain_int", "nap_rag_monitoring.csv")
    a.put("mu_rag_overall", mu_rag["overall_rag_summary"], "str", "nap_rag_monitoring.csv")
    a.put("kpi_dictionary_count", len(df_dict), "plain_int", "kpi_dictionary.csv")

    inst_only = df_rag[df_rag["entity_type"] == "Institution"]
    a.put("sector_rag_overall_green_insts", int((inst_only["overall_rag_summary"] == "GREEN").sum()), "plain_int", "nap_rag_monitoring.csv")
    a.put("sector_rag_overall_amber_insts", int((inst_only["overall_rag_summary"] == "AMBER").sum()), "plain_int", "nap_rag_monitoring.csv")
    a.put("sector_rag_overall_red_insts", int((inst_only["overall_rag_summary"] == "RED").sum()), "plain_int", "nap_rag_monitoring.csv")

    a.save(["outputs/kpis/kpi_dictionary.csv", "outputs/kpis/nap_rag_monitoring.csv"])
    return {"dictionary": df_dict, "rag_monitoring": df_rag}
