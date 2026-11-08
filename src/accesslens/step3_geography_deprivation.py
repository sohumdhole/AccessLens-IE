"""Step 3: Geography and deprivation (enrolments by home county for Irish-domiciled students
per relevant population against population-weighted county deprivation; Pearson and Spearman
correlations with 95% confidence intervals and explicit ecological-level framing).
"""
from __future__ import annotations

import math
import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from .audit import Audit
from .config import ACADEMIC_YEARS, IUA_UNIVERSITIES, OUT, WAREHOUSE


def _pearson_ci(x: np.ndarray, y: np.ndarray, alpha: float = 0.05) -> tuple[float, float, float, float]:
    r, p = stats.pearsonr(x, y)
    n = len(x)
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    z_crit = stats.norm.ppf(1.0 - alpha / 2.0)
    lo = math.tanh(z - z_crit * se)
    hi = math.tanh(z + z_crit * se)
    return float(r), float(lo), float(hi), float(p)


def _spearman_ci(
    x: np.ndarray, y: np.ndarray, n_boot: int = 5000, seed: int = 42
) -> tuple[float, float, float, float]:
    rho, p = stats.spearmanr(x, y)
    rng = np.random.default_rng(seed)
    n = len(x)
    boots = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(x[idx])) < 3 or len(np.unique(y[idx])) < 3:
            boots[i] = rho
        else:
            boots[i] = stats.spearmanr(x[idx], y[idx]).statistic
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(rho), float(lo), float(hi), float(p)


def run() -> dict:
    a = Audit("step3_geography_deprivation")
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    df_cty = con.execute("SELECT * FROM gold.fact_county_deprivation ORDER BY county").df()
    df_flow = con.execute("SELECT * FROM gold.fact_county_institution_year").df()
    con.close()

    geo_dir = OUT / "geography"
    geo_dir.mkdir(parents=True, exist_ok=True)

    # 1. Rank counties by population-weighted relative deprivation and 2025/2026 participation
    df_cty["deprivation_rank_most_disadvantaged_1"] = (
        df_cty["pop_wt_rel_deprivation"].rank(method="min", ascending=True).astype(int)
    )
    df_cty["enrol_rate_rank_highest_1_2025_26"] = (
        df_cty["enrol_per_1k_pop_2025_2026"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    df_cty["enrol_6yr_growth_pct"] = (
        df_cty["hea_enrol_2025_2026"] - df_cty["hea_enrol_2019_2020"]
    ) / df_cty["hea_enrol_2019_2020"]
    df_cty["mu_enrol_6yr_growth_pct"] = (
        df_cty["mu_enrol_2025_2026"] - df_cty["mu_enrol_2019_2020"]
    ) / df_cty["mu_enrol_2019_2020"].replace(0, np.nan)

    df_cty.to_csv(geo_dir / "county_deprivation_enrolments.csv", index=False)

    # 2. Compute correlations with 95% CIs across all 7 academic years and key indicators
    corr_rows = []
    x_rel = df_cty["pop_wt_rel_deprivation"].to_numpy(dtype=float)
    x_abs = df_cty["pop_wt_abs_deprivation"].to_numpy(dtype=float)
    x_dis_sh = df_cty["disadvantaged_pop_share"].to_numpy(dtype=float)
    x_edhigh = df_cty["pop_wt_edhigh22_pct"].to_numpy(dtype=float)

    for yr in ACADEMIC_YEARS:
        ys = yr.replace("/", "_")
        y_rate = df_cty[f"enrol_per_1k_pop_{ys}"].to_numpy(dtype=float)
        r, r_lo, r_hi, r_p = _pearson_ci(x_rel, y_rate)
        rho, s_lo, s_hi, s_p = _spearman_ci(x_rel, y_rate)
        slope, intercept, _, _, std_err = stats.linregress(x_rel, y_rate)
        corr_rows.append(
            {
                "analysis_id": f"rel_deprivation_vs_enrol_per_1k_{ys}",
                "academic_year": yr,
                "x_variable": "Population-weighted Pobal HP Relative Deprivation Score (2022)",
                "y_variable": f"Irish-domiciled HE enrolments per 1,000 population ({yr})",
                "n_counties": len(df_cty),
                "grain": "County-level ecological (26 counties of Ireland; not student-level)",
                "pearson_r": r,
                "pearson_ci95_low": r_lo,
                "pearson_ci95_high": r_hi,
                "pearson_p_value": r_p,
                "spearman_rho": rho,
                "spearman_ci95_low": s_lo,
                "spearman_ci95_high": s_hi,
                "spearman_p_value": s_p,
                "ols_slope_per_1pt_index": float(slope),
                "ols_intercept": float(intercept),
                "ols_r_squared": float(r * r),
            }
        )

    # Additional 2025/2026 ecological relationships
    y_rate_25 = df_cty["enrol_per_1k_pop_2025_2026"].to_numpy(dtype=float)
    extra_pairs = [
        (
            "abs_deprivation_vs_enrol_per_1k_2025_2026",
            "2025/2026",
            x_abs,
            "Population-weighted Pobal HP Absolute Deprivation Score (2022)",
            "Irish-domiciled HE enrolments per 1,000 population (2025/2026)",
        ),
        (
            "disadv_ed_pop_share_vs_enrol_per_1k_2025_2026",
            "2025/2026",
            x_dis_sh,
            "Share of county population in Disadvantaged/Very/Extremely Disadvantaged EDs (2022)",
            "Irish-domiciled HE enrolments per 1,000 population (2025/2026)",
        ),
        (
            "census_edhigh22_vs_enrol_per_1k_2025_2026",
            "2025/2026",
            x_edhigh,
            "County population-weighted adult third-level attainment EDHIGH22 % (2022)",
            "Irish-domiciled HE enrolments per 1,000 population (2025/2026)",
        ),
    ]
    for aid, yr, xv, xlab, ylab in extra_pairs:
        r, r_lo, r_hi, r_p = _pearson_ci(xv, y_rate_25)
        rho, s_lo, s_hi, s_p = _spearman_ci(xv, y_rate_25)
        slope, intercept, _, _, _ = stats.linregress(xv, y_rate_25)
        corr_rows.append(
            {
                "analysis_id": aid,
                "academic_year": yr,
                "x_variable": xlab,
                "y_variable": ylab,
                "n_counties": len(df_cty),
                "grain": "County-level ecological (26 counties of Ireland; not student-level)",
                "pearson_r": r,
                "pearson_ci95_low": r_lo,
                "pearson_ci95_high": r_hi,
                "pearson_p_value": r_p,
                "spearman_rho": rho,
                "spearman_ci95_low": s_lo,
                "spearman_ci95_high": s_hi,
                "spearman_p_value": s_p,
                "ols_slope_per_1pt_index": float(slope),
                "ols_intercept": float(intercept),
                "ols_r_squared": float(r * r),
            }
        )

    df_corr = pd.DataFrame(corr_rows)
    df_corr.to_csv(geo_dir / "deprivation_correlations.csv", index=False)

    # 3. Maynooth University catchment profile across all 26 counties
    mu_tot_25 = float(df_cty["mu_enrol_2025_2026"].sum())
    mu_catchment = df_cty[
        [
            "county",
            "province",
            "pop_2022",
            "pop_wt_rel_deprivation",
            "disadvantaged_pop_share",
            "is_below_national_affluence",
            "hea_enrol_2019_2020",
            "hea_enrol_2025_2026",
            "enrol_per_1k_pop_2025_2026",
            "mu_enrol_2019_2020",
            "mu_enrol_2025_2026",
            "mu_share_of_county_2025_2026",
            "mu_per_1k_pop_2025_2026",
        ]
    ].copy()
    mu_catchment["share_of_mu_irish_enrolments_2025_26"] = (
        mu_catchment["mu_enrol_2025_2026"] / mu_tot_25
    )
    mu_catchment = mu_catchment.sort_values(
        "mu_enrol_2025_2026", ascending=False
    ).reset_index(drop=True)
    mu_catchment.to_csv(geo_dir / "maynooth_catchment_profile.csv", index=False)

    # Compare all 7 IUA universities on share of Irish county-mapped students from below-average affluence counties (< 0)
    dep_counties = set(df_cty[df_cty["is_below_national_affluence"]]["county"])
    flow_25 = df_flow[df_flow["academic_year"] == "2025/2026"].copy()
    flow_25["is_dep"] = flow_25["county"].isin(dep_counties)
    iua_dep_shares = {}
    for u in IUA_UNIVERSITIES:
        sub_u = flow_25[flow_25["institute"] == u]
        tot_u = float(sub_u["enrolments"].sum())
        dep_u = float(sub_u[sub_u["is_dep"]]["enrolments"].sum())
        iua_dep_shares[u] = (dep_u, tot_u, dep_u / tot_u if tot_u else 0.0)

    # -------------------------------------------------------------------------
    # RECORD AUDIT METRICS FOR STEP 3
    # -------------------------------------------------------------------------
    c_idx = df_corr.set_index("analysis_id")
    c25 = c_idx.loc["rel_deprivation_vs_enrol_per_1k_2025_2026"]
    c22 = c_idx.loc["rel_deprivation_vs_enrol_per_1k_2022_2023"]
    c19 = c_idx.loc["rel_deprivation_vs_enrol_per_1k_2019_2020"]
    c_ed = c_idx.loc["census_edhigh22_vs_enrol_per_1k_2025_2026"]

    a.put("corr_rel_2025_26_r", float(c25["pearson_r"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_ci_low", float(c25["pearson_ci95_low"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_ci_high", float(c25["pearson_ci95_high"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_p", float(c25["pearson_p_value"]), "d4", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_rho", float(c25["spearman_rho"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_rho_ci_low", float(c25["spearman_ci95_low"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_rho_ci_high", float(c25["spearman_ci95_high"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_rho_p", float(c25["spearman_p_value"]), "d4", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_slope", float(c25["ols_slope_per_1pt_index"]), "d2", "deprivation_correlations.csv")
    a.put("corr_rel_2025_26_r2", float(c25["ols_r_squared"]), "pct", "deprivation_correlations.csv")

    a.put("corr_rel_2022_23_r", float(c22["pearson_r"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2022_23_ci_low", float(c22["pearson_ci95_low"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2022_23_ci_high", float(c22["pearson_ci95_high"]), "d3", "deprivation_correlations.csv")
    a.put("corr_rel_2022_23_p", float(c22["pearson_p_value"]), "d4", "deprivation_correlations.csv")
    a.put("corr_rel_2019_20_r", float(c19["pearson_r"]), "d3", "deprivation_correlations.csv")
    a.put("corr_edhigh_2025_26_r", float(c_ed["pearson_r"]), "d3", "deprivation_correlations.csv")

    cty_idx = df_cty.set_index("county")
    # Record all 26 counties in audit.json
    for c_name in sorted(cty_idx.index):
        slug = c_name.lower().replace(" ", "_")
        row = cty_idx.loc[c_name]
        a.put(f"cty_{slug}_pop22", int(round(row["pop_2022"])), "int", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_rel_score", float(row["pop_wt_rel_deprivation"]), "signed_d2", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_disadv_share", float(row["disadvantaged_pop_share"]), "pct", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_enrol_2025_26", int(row["hea_enrol_2025_2026"]), "int", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_rate_1k_2025_26", float(row["enrol_per_1k_pop_2025_2026"]), "d1", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_mu_2025_26", int(row["mu_enrol_2025_2026"]), "int", "county_deprivation_enrolments.csv")
        a.put(f"cty_{slug}_mu_share_2025_26", float(row["mu_share_of_county_2025_2026"]), "pct", "county_deprivation_enrolments.csv")

    n_dep_counties = int(df_cty["is_below_national_affluence"].sum())
    n_aff_counties = int((~df_cty["is_below_national_affluence"]).sum())
    dep_sub = df_cty[df_cty["is_below_national_affluence"]]
    aff_sub = df_cty[~df_cty["is_below_national_affluence"]]
    pooled_dep_rate = float(dep_sub["hea_enrol_2025_2026"].sum() / (dep_sub["pop_2022"].sum() / 1000.0))
    pooled_aff_rate = float(aff_sub["hea_enrol_2025_2026"].sum() / (aff_sub["pop_2022"].sum() / 1000.0))
    nat_mapped_25 = int(df_cty["hea_enrol_2025_2026"].sum())
    nat_rate_25 = float(nat_mapped_25 / (df_cty["pop_2022"].sum() / 1000.0))

    a.put("n_deprived_counties", n_dep_counties, "plain_int", "county_deprivation_enrolments.csv")
    a.put("n_affluent_counties", n_aff_counties, "plain_int", "county_deprivation_enrolments.csv")
    a.put("pooled_deprived_counties_rate_1k_2025_26", pooled_dep_rate, "d1", "county_deprivation_enrolments.csv")
    a.put("pooled_affluent_counties_rate_1k_2025_26", pooled_aff_rate, "d1", "county_deprivation_enrolments.csv")
    a.put("national_county_mapped_enrol_2025_26", nat_mapped_25, "int", "county_deprivation_enrolments.csv")
    a.put("national_enrol_rate_1k_2025_26", nat_rate_25, "d1", "county_deprivation_enrolments.csv")

    # Maynooth University catchment aggregates
    mu_dep_enrol, mu_map_tot, mu_dep_sh = iua_dep_shares["Maynooth University"]
    core3_enrol = int(
        cty_idx.loc[["Dublin", "Kildare", "Meath"], "mu_enrol_2025_2026"].sum()
    )
    a.put("mu_county_mapped_2025_26", int(mu_map_tot), "int", "maynooth_catchment_profile.csv")
    a.put("mu_core3_enrol_2025_26", core3_enrol, "int", "maynooth_catchment_profile.csv")
    a.put("mu_core3_share_2025_26", float(core3_enrol / mu_map_tot), "pct", "maynooth_catchment_profile.csv")
    a.put("mu_deprived_county_enrol_2025_26", int(mu_dep_enrol), "int", "maynooth_catchment_profile.csv")
    a.put("mu_deprived_county_share_2025_26", float(mu_dep_sh), "pct", "maynooth_catchment_profile.csv")
    a.put("dcu_deprived_county_share_2025_26", float(iua_dep_shares["Dublin City University"][2]), "pct", "maynooth_catchment_profile.csv")
    a.put("ucd_deprived_county_share_2025_26", float(iua_dep_shares["University College Dublin"][2]), "pct", "maynooth_catchment_profile.csv")
    a.put("tcd_deprived_county_share_2025_26", float(iua_dep_shares["Trinity College Dublin"][2]), "pct", "maynooth_catchment_profile.csv")

    a.save(
        [
            "outputs/geography/county_deprivation_enrolments.csv",
            "outputs/geography/deprivation_correlations.csv",
            "outputs/geography/maynooth_catchment_profile.csv",
        ]
    )
    return {
        "county_deprivation": df_cty,
        "correlations": df_corr,
        "maynooth_catchment": mu_catchment,
    }
