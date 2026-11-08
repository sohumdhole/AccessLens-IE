# Technical & Statistical Methodology

**Project:** AccessLens-IE  
**Author:** Sohum Vivek Dhole  
**Policy Reference:** National Access Plan (NAP) 2022-2028 (Higher Education Authority / Department of Further and Higher Education, Research, Innovation and Science)

---

## 1. Data Acquisition & Provenance Architecture

AccessLens-IE ingests **`52`** real, public statistical exports (**`620,916`** bytes total) with full cryptographic provenance recorded in [`outputs/audit/manifest.json`](../outputs/audit/manifest.json):

1. **HEA Student Records System (SRS) Public Releases (`2019/2020` to `2025/2026`):**
   * Extracted from the official HEA `Access our Data - Students` interactive portal (`https://hea.ie/statistics/data-for-download-and-visualisations/access-our-data/access-our-data-students/`, backed by `https://highereducationauthority.shinyapps.io/Enrolments_2026/`).
   * **`51` CSV files** covering all **`7`** academic years (`2019/2020` through `2025/2026`):
     * Multi-year series by `Institute` (`tab1_Institute_by_year.csv`, **`4,106`** bytes, SHA-256 prefix `de86a56cf25517c3`), `Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`, `Domicile Group`, `Gender`, and Irish-domiciled `County` (`tab1_County_IE_by_year.csv`, **`1,406`** bytes, SHA-256 prefix `b8cb7f49a72acff6`).
     * Annual two-way cross-tabulations across each of the **`7`** years for `Institute x Programme Type`, `Institute x Age Group`, `Institute x Mode of Study`, `Institute x Field of Study`, `Institute x Course Level`, and Irish-domiciled `County x Institute`.
2. **Pobal HP Deprivation Index Scores 2022 (Electoral Division Level, CC BY 4.0):**
   * Downloaded from `https://data.gov.ie/dataset/pobal-hp-deprivation-index-scores-2022` (`hp-deprivation-index-scores-2022.csv`, **`432,836`** bytes, SHA-256 prefix `48288b0651c63c5e`).
   * Contains **`3,417`** Electoral Divisions (EDs) across all **`26`** counties of the Republic of Ireland, including embedded CSO Census 2022 total population (`TOTPOP22`, summing to **`5,149,139`** residents), relative deprivation score (`Index22_ED_std_rel_wt`), absolute deprivation score (`Index22_ED_std_abs_wt`), third-level education share (`EDHIGH22`), primary-only education share (`EDLOW_22`), lone parent ratio (`LONEPA22`), and male/female unemployment rates (`UNEMPM22`, `UNEMPF22`).

---

## 2. DuckDB Medallion Architecture (Step 1)

`src/accesslens/step1_data_layer.py` builds a three-layer DuckDB analytical warehouse (`warehouse/accesslens.duckdb`):

### 2.1 Bronze Layer (`bronze.*`)
* Ingests all **`51`** HEA CSVs and the Pobal 2022 CSV without row deletion, attaching source filename and SHA-256 digest metadata to every record (`bronze.hea_tab1_multi_year`, `bronze.hea_inst_cross_year` with **`11,932`** raw cross-tabulation cells, `bronze.hea_county_inst_year`, and `bronze.pobal_ed_2022` with **`3,417`** EDs).

### 2.2 Silver Layer (`silver.*`) & Formal Data Quality Quarantine Rules
Six automated data-quality rules (`outputs/kpis/dq_rule_results.csv`) govern the transition from Bronze to Silver:

| Rule ID | Layer | Scope Checked | Flagged / Quarantined | Engineering Action |
| :--- | :--- | ---: | ---: | :--- |
| **DQ01_SUBTOTAL_SEPARATION** | Bronze -> Silver | `11,932` cells | `6,058` subtotal/total cells | Quarantined to `silver.quarantine_summary_rows`; **`5,874`** atomic cells retained in `silver.hea_inst_cross_clean`. |
| **DQ02_COUNTY_UNMAPPED_QUARANTINE** | Bronze -> Silver | County-year rows | `14` cells (`750` students over `7` yrs; `145` in `2025/2026`) | Quarantined `N/A` and `Unknown Ireland` domicile rows to `silver.quarantine_unmapped_county`. |
| **DQ03_CROSS_TAB_ADDITIVITY_RECONCILIATION** | Silver | Institution-year-dimension tables | `890` within `10`; max diff `15` | Verified sum of atomic cells against published `Row_Total` within HEA nearest-`5` rounding tolerance. |
| **DQ04_NCI_SCOPE_TRANSITION_FLAG** | Silver -> Gold | `182` institution-years | `4` pre-scope zero years | Flagged National College of Ireland (`2019/2020` to `2022/2023`) with `in_hea_scope = FALSE` prior to entering SRS scope in `2023/2024`. |
| **DQ05_POBAL_ED_COUNTY_COMPLETENESS** | Bronze -> Silver | `3,417` EDs | `0` unmapped EDs | Deterministic `27`-prefix CSO `ED_ID_STR` mapping to `26` counties (`silver.county_mapping`). |
| **DQ06_SMALL_CELL_SUPPRESSION** | Silver -> Gold | Atomic cross-tab + county flow cells | `206` small cells (`72` inst-dim + `134` county-inst) | Flagged `0 < count < 10` (`count == 5`) with `suppressed_lt10 = TRUE` and `display_enrolments = '<10'`. |

### 2.3 Deterministic County Mapping (`outputs/kpis/county_mapping.csv`)
The Pobal 2022 Electoral Division file identifies each ED by a 6-character CSO code (`ED_ID_STR`, zero-padded to 6 digits) where the first two digits denote the CSO administrative county (`01` Carlow through `26` Roscommon, plus `47` for Donegal alongside `25`). Mapping on the two-digit CSO prefix rather than text parsing of `COUNTYNAME` avoids substring collisions (for example, `Dublin` vs `South Dublin` or `Cork City` vs `Cork County`) and maps all **`3,417`** EDs (`5,149,139` population) across the **`26`** Republic of Ireland counties with zero unmapped records.

### 2.4 Gold Layer (`gold.*`)
* `gold.fact_institution_year` (**`182`** rows = `26` institutions x `7` academic years)
* `gold.fact_institution_dimension_year` (**`5,874`** atomic rows across Programme Type, Age Group, Mode of Study, Field of Study, and Course Level)
* `gold.fact_county_deprivation` (**`26`** counties with population-weighted Pobal 2022 indices)
* `gold.fact_county_institution_year` (**`4,628`** county-to-institution flow records across `7` years)

---

## 3. Institutional Benchmarking & Sector Taxonomy (Step 2)

To place **Maynooth University** in comparative context across **`7`** academic years (`2019/2020` to `2025/2026`), institutions are grouped into three reporting tiers:

1. **Maynooth University** (`15,945` enrolments in `2025/2026`, up **`+22.6%`** from `13,005` in `2019/2020`).
2. **IUA Universities (`7` universities + RCSI):** Maynooth University, University College Dublin, University of Galway, University College Cork, Trinity College Dublin, Dublin City University, University of Limerick, and RCSI (full institution-level figures in `outputs/kpis/university_peer_scorecard_2025_26.csv`), totalling **`157,495`** enrolments in `2025/2026` (**`+17.7%`** 6-year growth from **`133,780`**).
3. **All HEA Institutions (`26` institutions):** All IUA universities, all 5 Technological Universities (`TU Dublin`, `MTU`, `ATU`, `SETU`, `TUS`), Institutes of Technology (`DKIT`, `IADT`), Education & Specialist Colleges (`Mary Immaculate College`, `St. Angela's College`, `NCAD`, `NCI`, and constituent colleges), totalling **`283,940`** enrolments in `2025/2026` (**`+15.1%`** 6-year growth from **`246,635`**).

### Access Pathway Definitions
* **Standalone SRS `Foundation and Access`:** Enrolments coded directly under `Programme Type = Foundation and Access` (`1,035` nationally in `2025/2026`; `20` at Maynooth University).
* **Broad Non-Honours Undergraduate Pathway (`ug_access_pathway_enrolments`):** Sum of `Foundation and Access`, `Undergraduate Certificate`, `Undergraduate Diploma`, `Ordinary Degree`, and `Other Undergraduate` (`880` at Maynooth University in `2025/2026`, or **`6.6%`** of MU's **`13,310`** undergraduates, compared with **`8.8%`** across IUA universities and **`21.7%`** across all HEA institutions).

---

## 4. Population-Weighted County Deprivation & Ecological Correlation (Step 3)

For each county $c \in \{1, \dots, 26\}$ containing Electoral Divisions $e \in E_c$ with Census 2022 population $P_e$ (`TOTPOP22`) and Pobal HP 2022 relative deprivation score $D_e$ (`Index22_ED_std_rel_wt`), the population-weighted county score is computed as:

$$\bar{D}_c = \frac{\sum_{e \in E_c} P_e \, D_e}{\sum_{e \in E_c} P_e}$$

And the countyHigher Education Participation Rate per `1,000` residents in academic year $t$ is:

$$R_{c,t} = \frac{\text{Enrolments}_{c,t}}{\sum_{e \in E_c} P_e} \times 1,000$$

### Statistical Inference (`outputs/geography/deprivation_correlations.csv`)
* **Pearson Linear Correlation ($r$):** Evaluated with exact two-sided $t$-distribution $p$-value and Fisher $z$-transformation 95% confidence interval:
  $$z = \text{arctanh}(r), \quad \text{SE}(z) = \frac{1}{\sqrt{n - 3}}, \quad \text{CI}_{95\%} = \tanh\!\left(z \pm 1.96 \, \text{SE}(z)\right)$$
* **Spearman Rank Correlation ($\rho$):** Evaluated with two-sided $p$-value and non-parametric percentile bootstrap 95% confidence interval (`10,000` resamples, fixed seed `42`).
* **Audited Results (`2025/2026`, $n = 26$ counties):**
  * **Pobal Relative Score (`Index22_ED_std_rel_wt`) vs Enrolments per `1,000`:** Pearson $r = 0.680$ (95% CI **`0.397` to `0.845`**, $p = 0.0001$), Spearman $\rho = 0.693$ (95% CI **`0.371` to `0.883`**, $p = 0.0001$), OLS slope **`1.32`** enrolments per `1,000` per index point ($R^2 = 46.2%$).
  * **Census Match Year (`2022/2023`, $n = 26$ counties):** Pearson $r = 0.556$ (95% CI **`0.215` to `0.776`**, $p = 0.0032$).
  * **Pooled County Groups (`2025/2026`):** The **`7`** net-affluent counties (`Pobal score >= 0`) record a pooled rate of **`47.6`** per `1,000`, compared with **`44.3`** per `1,000` across the **`19`** below-average counties (`Pobal score < 0`).

---

## 5. National Access Plan 2022-2028 KPI & RAG Framework (Step 4)

The National Access Plan 2022-2028 sets headline national targets including:
* Raising the higher education transition rate from disadvantaged areas from **`42%`** to **`54%`**.
* Raising mature disadvantaged new entrants from **`11%`** to **`20%`**.
* Raising new entrants with a disability from **`12.4%`** to **`16%`**.
* Raising Traveller new entrants from **`33`** to **`150`**.

Source: HEA, National Access Plan launch announcement (https://hea.ie/2022/08/31/minister-harris-launches-the-new-national-access-plan-to-drive-equality-of-access-to-higher-education/). The Education and Social Sciences field share is reported as a context indicator only and is not RAG-scored.

Because public SRS aggregate tables do not expose student-level Eircode deprivation or disability status, `src/accesslens/step4_kpi_framework.py` maps **`6`** public SRS indicators to NAP priority goals with explicit `GREEN`, `AMBER`, and `RED` thresholds (`outputs/kpis/kpi_dictionary.csv` and `outputs/kpis/nap_rag_monitoring.csv`).
