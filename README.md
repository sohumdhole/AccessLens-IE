# AccessLens-IE: Widening Participation, Access Pathways & Geographic Deprivation Analytics for Irish Higher Education (2019/2020 to 2025/2026)

[![License: MIT](https://img.shields.io/badge/Code_License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](requirements.txt)
[![DuckDB](https://img.shields.io/badge/Warehouse-DuckDB_Medallion-FFF000.svg)](src/accesslens/step1_data_layer.py)
[![NAP 2022-2028](https://img.shields.io/badge/Policy-National_Access_Plan_2022--2028-006644.svg)](docs/methodology.md)

**Author:** Sohum Vivek Dhole (MSc Business Analytics, First Class Honours; BE Electronics Engineering)

**AccessLens-IE** is an end-to-end, reproducible analytics engineering and widening participation reporting pipeline built on official **Higher Education Authority (HEA)** Student Records System (SRS) public releases (`2019/2020` to `2025/2026`, `51` CSV tables) and the **Pobal HP Deprivation Index 2022** at Electoral Division grain (`3,417` Electoral Divisions covering all `5,149,139` Census 2022 residents across `26` counties).

The project evaluates higher education access pathways, mature student participation, flexible/part-time study modes, discipline mix, and county-level socio-economic catchment profiles, benchmarking **Maynooth University (MU)** against the **IUA University Sector (`7` universities)** and the **All HEA-Funded Institutions (`26` institutions)** benchmark under the **National Access Plan (NAP) 2022-2028** indicator framework.

Every figure in this repository is rendered directly from [`outputs/audit/audit.json`](outputs/audit/audit.json) and verified by an automated `pytest` suite covering data contracts, DuckDB metric recomputation, document traceability, mutation testing, GDPR-style small-cell suppression (`<10`), and formula-driven Excel/Power BI delivery.

---

## Headline Audited Findings (`2019/2020` to `2025/2026`)

1. **Sustained Enrolment Expansion Outpacing Sector Benchmarks:** Maynooth University grew from **`13,005`** total enrolments in `2019/2020` to **`15,945`** in `2025/2026` (adding **`2,940`** students, **`+22.6%`** over six years and **`+2.5%`** year-on-year from **`15,560`** in `2024/2025`). This outpaced both the `7`-university IUA group (**`+17.7%`**, from **`133,780`** to **`157,495`**) and the full `26`-institution HEA sector (**`+15.1%`**, from **`246,635`** to **`283,940`**).
2. **Mature and Flexible Participation Composition Shift:** While Maynooth University's absolute mature (`24+`) student headcount held steady around three thousand students (**`3,195`** in `2019/2020`, **`3,250`** in `2024/2025`, and **`3,140`** in `2025/2026`), rapid expansion in young (`23 and under`) undergraduate Honours Degree entrants (**`+30.5%`**, from **`9,810`** to **`12,805`**) shifted MU's mature student share from **`24.6%`** to **`19.7%`** (**`-4.9 pp`**), compared with **`30.7%`** across IUA universities and **`34.8%`** across all HEA institutions. Part-time and flexible delivery at MU represents **`10.4%`** (**`1,665`** students) in `2025/2026`, compared with **`15.3%`** in the university sector and **`21.8%`** across the HEA sector.
3. **Foundation, Access and Non-Honours Undergraduate Pathways vs Direct Degree Entry:** Across all HEA institutions, standalone `Foundation and Access` programme enrolments rose **`+31.0%`** over six years (from **`790`** in `2019/2020` to **`1,035`** in `2025/2026`), concentrated in institutions that code foundation certificates as standalone SRS programmes: **ATU Donegal (`470`)**, **TU Dublin City (`155`)**, **Trinity College Dublin (`140`)**, **University of Galway (`90`)**, and **MTU Kerry (`80`)**. At Maynooth University, standalone SRS `Foundation and Access` headcount is **`20`** (**`40`** in `2019/2020`), while broader non-honours undergraduate pathways (`Foundation and Access`, `Undergraduate Certificate`, `Undergraduate Diploma`, `Ordinary Degree`, and `Other Undergraduate`, including part-time certificates and partnership programmes) total **`880`** students (**`6.6%`** of MU's **`13,310`** undergraduates and **`5.5%`** of total enrolments). Honours Degrees account for **`78.0%`** (**`12,430`** students, up **`+28.7%`** from **`9,660`**). The public data cannot show which routes HEAR, DARE or FET entrants take.
4. **Ecological County Deprivation vs Higher Education Participation:** Across Ireland's `26` counties (`238,105` county-mapped Irish-domiciled enrolments in `2025/2026`, or **`46.2`** per `1,000` residents), county population-weighted Pobal HP relative deprivation score (`Index22_ED_std_rel_wt`) exhibits a statistically significant positive correlation with higher education participation per `1,000` residents: **Pearson $r = 0.680$** (95% CI **`0.397` to `0.845`**, $p = 0.0001$) and **Spearman $\rho = 0.693$** (95% CI **`0.371` to `0.883`**, $p = 0.0001$), with an OLS slope of **`1.32`** additional enrolments per `1,000` population per Pobal index point ($R^2 = 46.2%$). In the exact Census match year (`2022/2023`), Pearson $r = 0.556$ (95% CI **`0.215` to `0.776`**, $p = 0.0032$).
5. **Maynooth University's Midlands, Border and South-East Catchment Reach:** While **`62.1%`** (**`9,145`** of MU's **`14,720`** county-mapped Irish students) originate from the commuter core of **Dublin (`4,530`)**, **Kildare (`2,830`**, where MU educates **`22.0%`** of all higher education students from the county), and **Meath (`1,785`**, **`17.0%`** share), Maynooth draws **`4,775`** students (**`32.4%`**, rated **`GREEN`** against the **`20.0%`** target) from the **`19`** counties with below-average Pobal affluence (`score < 0`), substantially higher than Dublin university peers **DCU (`29.8%`)**, **UCD (`23.8%`)**, and **TCD (`20.2%`)**. This largely reflects Maynooth's location near the Midlands counties, not only institutional access activity. MU captures **`12.3%`** (**`245`**) of all HE students from **Co. Longford** (Pobal score **`-5.33`**), **`12.1%`** (**`590`**) from **Co. Westmeath** (**`-1.43`**), **`11.8%`** (**`365`**) from **Co. Cavan** (**`-3.99`**), **`11.6%`** (**`415`**) from **Co. Offaly** (**`-3.95`**), **`9.1%`** (**`145`**) from **Co. Leitrim** (**`-2.41`**), **`8.8%`** (**`350`**) from **Co. Laois** (**`-2.02`**), **`8.4%`** (**`570`**) from **Co. Wexford** (**`-4.09`**), and **`8.0%`** (**`240`**) from **Co. Carlow** (**`-2.76`**).

---

## Visual Summary

### 1. Maynooth University vs Sector Benchmarks (`2019/2020` to `2025/2026`)
![Maynooth University Benchmark Trends](outputs/figures/fig1_maynooth_benchmark_trends.png)

### 2. County Pobal HP Deprivation vs Higher Education Participation (`2025/2026`, Ecological)
![County Deprivation vs Enrolment Rate](outputs/figures/fig2_county_deprivation_scatter.png)

### 3. Maynooth University Geographic Catchment & Deprivation Profile (`2025/2026`)
![Maynooth Catchment Profile](outputs/figures/fig3_maynooth_catchment_profile.png)

### 4. National Access Plan (NAP) 2022-2028 Proxy KPI Scorecard (`2025/2026`)
![NAP RAG Scorecard](outputs/figures/fig4_nap_rag_scorecard.png)

---

## Key Benchmark Tables (`2025/2026` vs `2019/2020`)

### Table 1: Maynooth University vs University Sector and All HEA Institutions

| Metric | Maynooth University (`2019/2020`) | Maynooth University (`2024/2025`) | Maynooth University (`2025/2026`) | IUA Universities (`2025/2026`) | All HEA Institutions (`2025/2026`) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Total Enrolments** | `13,005` | `15,560` | `15,945` (`+22.6%` 6yr) | `157,495` (`+17.7%` 6yr) | `283,940` (`+15.1%` 6yr) |
| **Mature Students (`24+`)** | `3,195` (`24.6%`) | `3,250` (`20.9%`) | `3,140` (`19.7%`, `-4.9 pp`) | `30.7%` | `98,925` (`34.8%`) |
| **Part-Time / Flexible Study** | `1,740` (`13.4%`) | `1,535` (`9.9%`) | `1,665` (`10.4%`) | `15.3%` | `61,795` (`21.8%`) |
| **Standalone SRS `Foundation and Access`** | `40` | `20` | `20` | See peer breakdown | `1,035` (`+31.0%` 6yr) |
| **Non-Honours UG Pathways (% of UG)** |Tracked in KPI CSV | Tracked in KPI CSV | `880` (`6.6%`) | `8.8%` | `21.7%` |
| **Honours Degree Enrolments (% Total)** | `9,660` | Tracked in KPI CSV | `12,430` (`78.0%`, `+28.7%`) | Tracked in KPI CSV | `60.2%` |
| **Education & Social Care Field Share** | Tracked in KPI CSV | Tracked in KPI CSV | `3,150` (`19.8%`) | Tracked in KPI CSV | `12.9%` |
| **Deprived-County (`Pobal < 0`) Share** | Tracked in KPI CSV | Tracked in KPI CSV | `4,775` (`32.4%`) | DCU `29.8%` / UCD `23.8%` / TCD `20.2%` | `19` of `26` counties |

### Table 2: National Access Plan (NAP) 2022-2028 Proxy KPI & RAG Monitoring View for Maynooth University (`2025/2026`)

Public HEA SRS downloads do not expose individual-level deprivation, disability (DARE), or QQI/FET entry basis. AccessLens-IE defines **`6`** transparent institutional proxy KPIs mapped to NAP 2022-2028 goals (full definitions in [`outputs/kpis/kpi_dictionary.csv`](outputs/kpis/kpi_dictionary.csv) and [`outputs/kpis/nap_rag_monitoring.csv`](outputs/kpis/nap_rag_monitoring.csv)):

| KPI ID | KPI Name | NAP 2022-2028 Reference | Green Threshold | Amber Threshold | MU `2025/2026` Value | MU RAG Status |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| **KPI_01** | Standalone Foundation & Access Enrolments | Priority Group Entry Routes (NAP Goal 1) | Informational | Informational | `20` (Sector: `1,035`) | `INFO` |
| **KPI_02** | Non-Honours UG Pathway Share (% of UG) | Foundation and sub-degree entry routes (no numeric NAP target used) | `>= 8.0%` | `>= 5.0%` | `6.6%` (`880`) | **`AMBER`** |
| **KPI_03** | Mature Student (`24+`) Enrolment Share | Mature Disadvantaged Entrants (`11%` to `20%`) | `>= 25.0%` | `>= 18.0%` | `19.7%` (`3,140`) | **`AMBER`** |
| **KPI_04** | Flexible & Part-Time Study Share | Flexible & Lifelong Learning Provision (NAP Goal 2) | `>= 15.0%` | `>= 10.0%` | `10.4%` (`1,665`) | **`AMBER`** |
| **KPI_05** | Deprived-County (`Pobal < 0`) Catchment Share | Disadvantaged-Area Transition (`42%` to `54%`) | `>= 20.0%` | `>= 14.0%` | `32.4%` (`4,775`) | **`GREEN`** |
| **KPI_06** | Education & Social Sciences Field Share (context) | Context indicator only, not a widening participation measure | Not scored | Not scored | `19.8%` (`3,150`) | `CONTEXT` |

Across the `26` HEA institutions in `2025/2026`, **`20`** achieve an overall `GREEN` composite rating, **`4`** rate `AMBER` (including Maynooth University with **`1` GREEN**, **`3` AMBER**, and **`0` RED** KPIs), and **`2`** specialist colleges rate `RED`.

---

## Honest Analytical Boundaries & GDPR-Style Disclosure Control

Widening participation analytics requires strict separation between what public aggregate data can support and what requires restricted microdata. Detailed documentation is provided in [`docs/what_this_data_can_and_cannot_show.md`](docs/what_this_data_can_and_cannot_show.md):

1. **County-Level (Ecological) Deprivation, Not Individual-Level:** The Pobal HP 2022 link in Step 3 measures the socio-economic profile of a student's home county (`3,417` Electoral Divisions aggregated by Census 2022 population weights to `26` counties). Inferring that every student from a disadvantaged county is personally disadvantaged, or that students from affluent counties are personally affluent, is the **ecological fallacy**. Individual-level deprivation monitoring in Ireland uses the **HEA Deprivation Index Score (DIS)** linked to student home Eircodes/Small Areas inside institutional student records.
2. **No Disability or Ethnic Group Micro-Indicators in Public SRS Downloads:** Public HEA `Access our Data - Students` exports do not contain student disability status, DARE/HEAR indicator flags, QQI/FET basis of entry, or Irish Traveller / Roma identifiers. National Access Plan targets such as raising new entrants with disabilities to **`16%`** are recorded in the KPI dictionary as requiring internal Access Office or HEA Equal Access Survey (EAS) returns.
3. **Nearest-`5` Rounding and Small-Cell Suppression (`<10`):** Published HEA SRS counts are independently rounded to the nearest **`5`**. In addition, as a GDPR-style statistical disclosure control best practice, AccessLens-IE suppresses all non-zero cells below **`10`** (i.e. published cells equal to `5`) as `"<10"` in output display columns (`72` institution-dimension cells and `134` county-institution cells, totalling **`206`** flagged small cells).
4. **HEA-Funded Institutional Scope:** The dataset covers the **`26`** HEA-funded higher education institutions reporting to the SRS (`2019/2020` to `2025/2026`), noting that **National College of Ireland** entered SRS reporting scope in `2023/2024` (`4` structural zero years in `2019/2020` to `2022/2023` flagged in `gold.fact_institution_year`). Private/independent colleges outside HEA SRS are not included.
5. **Observational Patterns, No Causal Claims:** All correlations and comparisons reported in this repository are descriptive and observational.

---

## Repository Architecture (7 Fixed Steps)

```text
AccessLens-IE/
├── README.md                                  # Rendered from templates/README.md.tmpl via audit.json
├── LICENSE                                    # MIT License for project code
├── pytest.ini                                 # Pytest configuration
├── requirements.txt                           # Python dependencies
├── data/
│   └── raw/                                   # Excluded from Git via .gitignore (.gitkeep tracked)
├── warehouse/
│   └── accesslens.duckdb                      # Excluded from Git; Bronze/Silver/Gold DuckDB warehouse
├── src/
│   └── accesslens/
│       ├── config.py                          # Paths, sector taxonomy, 27 CSO county prefixes, NAP thresholds
│       ├── audit.py                           # Single-source audit registry (outputs/audit/audit.json)
│       ├── step1_data_layer.py                # Step 1: DuckDB Bronze/Silver/Gold, 6 DQ rules, suppression, manifest
│       ├── step2_access_indicators.py         # Step 2: Access KPIs, mature, flexible, field mix, MU benchmarks
│       ├── step3_geography_deprivation.py     # Step 3: Pobal ED-to-county weighting, Pearson/Spearman CIs, catchment
│       ├── step4_kpi_framework.py             # Step 4: NAP 2022-2028 KPI dictionary & RAG monitoring table
│       ├── step5_excel_powerbi.py             # Step 5: Formula-driven Excel pack & Power BI star-schema exports
│       ├── step6_docs.py                      # Step 6: Deterministic rendering of docs & DAX from audit.json
│       ├── viz.py                             # Publication-grade charts in outputs/figures/
│       └── pipeline.py                        # End-to-end orchestrator
├── templates/                                 # Audit-placeholder templates (.tmpl) for all docs and DAX
├── docs/
│   ├── methodology.md                         # Full technical & statistical methodology
│   ├── what_this_data_can_and_cannot_show.md  # Analytical boundaries, GDPR practice & ecological fallacy guide
│   ├── briefing_summary.md                    # One-page plain-English briefing for non-technical readers
│   └── powerbi_build_guide.md                 # Page-by-page Power BI build guide with check values
├── outputs/
│   ├── audit/
│   │   ├── audit.json                         # Single source of truth for all rendered numbers
│   │   └── manifest.json                      # Provenance manifest (URLs, timestamps, byte sizes, SHA-256)
│   ├── excel/
│   │   └── AccessLens_IE_KPI_Pack.xlsx        # 6-sheet workbook with 310 live formulas, dropdown & charts
│   ├── figures/                               # 4 PNG visualisations
│   ├── geography/                             # County deprivation, correlations & Maynooth catchment CSVs
│   ├── kpis/                                  # DQ rules, county mapping, institution KPIs, NAP RAG & dictionary CSVs
│   └── powerbi/                               # Star-schema CSV + Parquet tables & measures.dax
├── tools/
│   └── make_release.py                        # Builds clean GitHub release copy excluding raw data & DuckDB
└── tests/                                     # Pytest suite (data contracts, recomputation, traceability, hygiene)
```

---

## How to Run & Verify

### 1. Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Full 6-Step Analytics & Reporting Pipeline

When raw exports are present in `data/raw/`, rebuild the DuckDB warehouse, recompute all KPIs and correlations, regenerate charts, build the Excel workbook and Power BI star schema, and render all documentation from `outputs/audit/audit.json`:

```bash
python -m accesslens.pipeline
```

### 3. Run the Automated Test Suite (Step 7)

The `pytest` suite runs cleanly both in a full local checkout (with `warehouse/accesslens.duckdb`) and in the clean GitHub release copy (verifying committed gold CSVs, Excel formulas, Power BI schemas, document-to-audit traceability, and mutation detection):

```bash
pytest -q
```

---

## Data Sources, Provenance & Licences

Full file-by-file SHA-256 hashes, byte sizes (`620,916` total bytes across `52` raw files), download timestamps, and source URLs are recorded in [`outputs/audit/manifest.json`](outputs/audit/manifest.json):

* **Higher Education Authority (HEA) - "Access our Data: Students" (`2019/2020` to `2025/2026`):**
  * **Portal URL:** https://hea.ie/statistics/data-for-download-and-visualisations/access-our-data/access-our-data-students/
  * **Underlying Shiny Application Endpoint:** https://highereducationauthority.shinyapps.io/Enrolments_2026/
  * **Files Ingested:** `51` official CSV exports (`9` multi-year Tab 1 tables across all `7` academic years + `42` Tab 2 cross-tabulations covering `Institute x Programme Type`, `Institute x Age Group`, `Institute x Mode of Study`, `Institute x Field of Study`, `Institute x Course Level`, and Irish-domiciled `County x Institute`). Key anchor files include `tab1_Institute_by_year.csv` (`4,106` bytes, SHA-256 prefix `de86a56cf25517c3`) and `tab1_County_IE_by_year.csv` (`1,406` bytes, SHA-256 prefix `b8cb7f49a72acff6`).
  * **Terms of Use:** Public sector statistical data published by the Higher Education Authority for public information, research, and policy analysis under PSI / Open Data reuse principles, with source attribution to the HEA Student Records System (SRS).
* **Pobal HP Deprivation Index Scores 2022 (Electoral Division Level):**
  * **Dataset URL:** https://data.gov.ie/dataset/pobal-hp-deprivation-index-scores-2022
  * **File Ingested:** `hp-deprivation-index-scores-2022.csv` (`432,836` bytes, SHA-256 prefix `48288b0651c63c5e`, `3,417` Electoral Divisions with embedded CSO Census 2022 population `TOTPOP22 = 5,149,139`).
  * **Licence:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**, credited to Pobal, Haase & Pratschke (Trutz Haase & Jonathan Pratschke), and Central Statistics Office (CSO) Census 2022 boundary/population data.
* **National Access Plan (NAP) 2022-2028 Policy Targets:**
  * **Source URL:** https://hea.ie/2022/08/31/minister-harris-launches-the-new-national-access-plan-to-drive-equality-of-access-to-higher-education/
* **Repository Source Code:** Licensed under the **MIT License** ([`LICENSE`](LICENSE)).
