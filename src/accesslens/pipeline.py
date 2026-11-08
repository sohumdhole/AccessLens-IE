"""End-to-end deterministic execution pipeline for AccessLens-IE (Steps 1 through 6)."""
from __future__ import annotations

from . import (
    step1_data_layer,
    step2_access_indicators,
    step3_geography_deprivation,
    step4_kpi_framework,
    step5_excel_powerbi,
    step6_docs,
    viz,
)


def main():
    print("[Step 1/6] Building DuckDB bronze/silver/gold warehouse, DQ rules, county mapping, and manifest...")
    step1_data_layer.run()
    print("[Step 2/6] Computing institutional access indicators and Maynooth University benchmarks...")
    step2_access_indicators.run()
    print("[Step 3/6] Computing county-level Pobal deprivation correlations and Maynooth catchment profile...")
    step3_geography_deprivation.run()
    print("[Step 4/6] Building National Access Plan (2022-2028) KPI dictionary and RAG monitoring view...")
    step4_kpi_framework.run()
    print("[Viz] Rendering analytical figures...")
    viz.run()
    print("[Step 5/6] Building formula-driven Excel KPI pack and Power BI star-schema exports...")
    step5_excel_powerbi.run()
    print("[Step 6/6] Rendering README, methodology, briefing, Power BI guide, and DAX from audit.json...")
    step6_docs.run()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
