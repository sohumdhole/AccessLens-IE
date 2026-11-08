"""Generate publication-quality charts for README and documentation."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import IUA_UNIVERSITIES, OUT


def run():
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    kpi_dir = OUT / "kpis"
    geo_dir = OUT / "geography"

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # -------------------------------------------------------------------------
    # Figure 1: Maynooth University vs Sector Benchmarks (2019/20 to 2025/26)
    # -------------------------------------------------------------------------
    bench = pd.read_csv(kpi_dir / "maynooth_vs_benchmarks_by_year.csv")
    years = sorted(bench["academic_year"].unique())
    short_yrs = [y[:4] + "/" + y[7:] for y in years]

    groups_cfg = [
        ("Maynooth University", "#003865", "-", "o", 2.6),
        ("Traditional Universities (7 IUA)", "#2B7BBA", "--", "s", 2.0),
        ("All HEA Institutions (Sector)", "#6C757D", ":", "^", 2.0),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2), dpi=160)
    panels = [
        ("index_2019_20_eq_100", "A. Enrolment Growth Index (2019/20 = 100)", "Index (2019/20 = 100)", False),
        ("mature_24plus_share", "B. Mature Student Share (Age 24+, All Levels)", "Share of Total Enrolments (%)", True),
        ("flexible_share", "C. Part-Time & Flexible Study Share", "Share of Total Enrolments (%)", True),
        ("ug_access_pathway_share_of_ug", "D. Non-Honours & Foundation Share of UG", "Share of UG Enrolments (%)", True),
    ]

    for ax, (col, title, ylab, is_pct) in zip(axes.flat, panels):
        for gname, color, ls, marker, lw in groups_cfg:
            sub = bench[bench["benchmark_group"] == gname].sort_values("academic_year")
            vals = sub[col].to_numpy(dtype=float) * (100.0 if is_pct else 1.0)
            ax.plot(short_yrs, vals, label=gname, color=color, linestyle=ls, marker=marker, linewidth=lw, markersize=5.5)
            ax.annotate(
                f"{vals[-1]:.1f}{'%' if is_pct else ''}",
                xy=(len(short_yrs) - 1, vals[-1]),
                xytext=(5, 0),
                textcoords="offset points",
                fontsize=8.5,
                fontweight="bold" if gname == "Maynooth University" else "normal",
                color=color,
                va="center",
            )
        ax.set_title(title, loc="left", pad=8)
        ax.set_ylabel(ylab)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.margins(x=0.14)

    axes[0, 0].legend(loc="upper left", frameon=True, fontsize=8.8)
    fig.suptitle(
        "Maynooth University Enrolment Trajectory vs University & HEA Sector Benchmarks (2019/20 to 2025/26)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(fig_dir / "access_maynooth_vs_benchmarks.png")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figure 2: Field of Study Mix Comparison (2025/2026)
    # -------------------------------------------------------------------------
    fs = pd.read_csv(kpi_dir / "field_of_study_mix_comparison.csv")
    fs25 = fs[fs["academic_year"] == "2025/2026"].sort_values("maynooth_share", ascending=True)

    fig, ax = plt.subplots(figsize=(11.5, 6.4), dpi=160)
    y = np.arange(len(fs25))
    h = 0.27
    ax.barh(y + h, fs25["maynooth_share"] * 100.0, height=h, label="Maynooth University", color="#003865")
    ax.barh(y, fs25["iua_universities_share"] * 100.0, height=h, label="Traditional Universities (7 IUA)", color="#3B8BC2")
    ax.barh(y - h, fs25["hea_sector_share"] * 100.0, height=h, label="All HEA Sector", color="#ADB5BD")

    for i, v in enumerate(fs25["maynooth_share"] * 100.0):
        if v > 0.1:
            ax.text(v + 0.35, i + h, f"{v:.1f}%", va="center", fontsize=8.3, fontweight="bold", color="#003865")

    ax.set_yticks(y)
    ax.set_yticklabels(fs25["field_of_study"], fontsize=9.2)
    ax.set_xlabel("Share of Enrolments in 2025/2026 (%)")
    ax.set_title(
        "ISCED Field of Study Mix (2025/2026): Maynooth University vs Traditional Universities and HEA Sector",
        loc="left",
        pad=10,
    )
    ax.set_xlim(0, 36)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.legend(loc="lower right", frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "access_field_of_study_mix.png")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figure 3: Geography & Deprivation (Ecological Correlation & MU Catchment)
    # -------------------------------------------------------------------------
    cty = pd.read_csv(geo_dir / "county_deprivation_enrolments.csv")
    corr = pd.read_csv(geo_dir / "deprivation_correlations.csv").set_index("analysis_id")
    c25 = corr.loc["rel_deprivation_vs_enrol_per_1k_2025_2026"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.8), dpi=160)

    x = cty["pop_wt_rel_deprivation"].to_numpy(dtype=float)
    y_rate = cty["enrol_per_1k_pop_2025_2026"].to_numpy(dtype=float)
    colors = np.where(x < 0, "#D95F02", "#1B9E77")
    sizes = np.clip(cty["pop_2022"].to_numpy(dtype=float) / 3000.0, 35, 260)

    ax1.scatter(x, y_rate, c=colors, s=sizes, alpha=0.82, edgecolors="black", linewidth=0.6)
    xs = np.linspace(x.min() - 0.4, x.max() + 0.4, 100)
    ys = c25["ols_intercept"] + c25["ols_slope_per_1pt_index"] * xs
    ax1.plot(xs, ys, color="#003865", linestyle="--", linewidth=1.8, label=f"OLS trend (r = {c25['pearson_r']:.2f}, p = {c25['pearson_p_value']:.4f})")
    ax1.axvline(0.0, color="#888888", linestyle=":", linewidth=1.0)

    label_counties = {
        "Donegal", "Longford", "Wexford", "Cavan", "Offaly", "Monaghan",
        "Louth", "Westmeath", "Galway", "Kildare", "Dublin", "Meath", "Cork", "Clare"
    }
    for _, r in cty.iterrows():
        if r["county"] in label_counties:
            ax1.annotate(
                r["county"],
                (r["pop_wt_rel_deprivation"], r["enrol_per_1k_pop_2025_2026"]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=8.2,
            )

    ax1.set_title("A. County Deprivation vs HE Enrolments per 1,000 Pop (2025/26)", loc="left")
    ax1.set_xlabel("Population-Weighted Pobal HP Relative Score 2022 (<0 = More Disadvantaged)")
    ax1.set_ylabel("Irish-Domiciled HE Enrolments per 1,000 County Residents")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="lower right", frameon=True, fontsize=8.8)

    # Panel B: Top 12 counties by Maynooth share of county HE enrolments in 2025/2026
    top_mu = cty.sort_values("mu_share_of_county_2025_2026", ascending=True).tail(12)
    bar_colors = np.where(top_mu["pop_wt_rel_deprivation"] < 0, "#D95F02", "#003865")
    y_pos = np.arange(len(top_mu))
    vals_mu = top_mu["mu_share_of_county_2025_2026"].to_numpy(dtype=float) * 100.0
    ax2.barh(y_pos, vals_mu, color=bar_colors, alpha=0.88, edgecolor="black", linewidth=0.5)
    for i, (_, r) in enumerate(top_mu.iterrows()):
        v = r["mu_share_of_county_2025_2026"] * 100.0
        sc = r["pop_wt_rel_deprivation"]
        ax2.text(
            v + 0.3,
            i,
            f"{v:.1f}% ({int(r['mu_enrol_2025_2026']):,} students | Pobal {sc:+.2f})",
            va="center",
            fontsize=8.0,
        )
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top_mu["county"], fontsize=9.2)
    ax2.set_xlim(0, 31)
    ax2.set_xlabel("Maynooth University Share of County HE Enrolments (%)")
    ax2.set_title("B. Maynooth Share of County HE Enrolments (Orange = Pobal Score < 0)", loc="left")
    ax2.grid(axis="x", linestyle="--", alpha=0.3)

    fig.suptitle(
        "County-Level (Ecological) Deprivation Gradient and Maynooth University Regional Reach",
        fontsize=12.5,
        fontweight="bold",
        y=0.99,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(fig_dir / "geo_deprivation_vs_enrolment.png")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figure 4: National Access Plan KPI RAG Monitoring Scorecard (2025/2026)
    # -------------------------------------------------------------------------
    rag = pd.read_csv(kpi_dir / "nap_rag_monitoring.csv")
    focus_entities = IUA_UNIVERSITIES + [
        "Traditional Universities (7 IUA)",
        "Technological Universities / IoTs",
        "All HEA Institutions (Sector)",
    ]
    sub_rag = rag[rag["institute"].isin(focus_entities)].copy()
    order_map = {name: i for i, name in enumerate(focus_entities)}
    sub_rag["sort_key"] = sub_rag["institute"].map(order_map)
    sub_rag = sub_rag.sort_values("sort_key").reset_index(drop=True)

    kpi_cols = [
        ("mature_share", "rag_mature_share", "Mature (24+)\nShare"),
        ("flexible_share", "rag_flexible_share", "Flexible / PT\nShare"),
        ("ug_access_pathway_share_ug", "rag_ug_pathway_breadth", "UG Access &\nCert Pathway"),
        ("deprived_county_share", "rag_deprived_county_reach", "Deprived-County\nReach (<0)"),
    ]
    color_map = {"GREEN": "#C8E6C9", "AMBER": "#FFE0B2", "RED": "#FFCDD2"}
    text_color_map = {"GREEN": "#1B5E20", "AMBER": "#E65100", "RED": "#B71C1C"}

    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=160)
    n_rows = len(sub_rag)
    n_cols = len(kpi_cols)
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.invert_yaxis()

    for r_idx, (_, row) in enumerate(sub_rag.iterrows()):
        for c_idx, (vcol, rcol, _) in enumerate(kpi_cols):
            status = row[rcol]
            val = row[vcol] * 100.0
            bg = color_map.get(status, "#EEEEEE")
            fg = text_color_map.get(status, "#333333")
            rect = plt.Rectangle((c_idx, r_idx), 1, 1, facecolor=bg, edgecolor="white", linewidth=2.0)
            ax.add_patch(rect)
            ax.text(
                c_idx + 0.5,
                r_idx + 0.48,
                f"{val:.1f}%\n({status})",
                ha="center",
                va="center",
                fontsize=8.8,
                fontweight="bold" if row["institute"] == "Maynooth University" else "normal",
                color=fg,
            )

    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels([c[2] for c in kpi_cols], fontsize=9.5, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ylabels = [
        f">>> {r['institute']} <<<" if r["institute"] == "Maynooth University" else r["institute"]
        for _, r in sub_rag.iterrows()
    ]
    ax.set_yticklabels(ylabels, fontsize=9.2)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    fig.suptitle(
        "National Access Plan (NAP 2022-2028) Public SRS Proxy KPI Monitoring View (2025/2026)",
        fontsize=12,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(fig_dir / "kpi_rag_scorecard.png")
    plt.close(fig)
