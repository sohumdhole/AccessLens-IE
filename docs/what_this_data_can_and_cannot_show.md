# What Public HEA & Pobal Data Can and Cannot Show: Analytical Boundaries & Ethical Data Practice

**Project:** AccessLens-IE  
**Author:** Sohum Vivek Dhole  
**Context:** Widening Participation & Higher Education Policy Analytics (National Access Plan 2022-2028)

A core competency in higher education widening participation analytics is distinguishing what **public aggregate statistical releases** can rigorously answer from what requires **student-level microdata** governed by institutional GDPR data protection frameworks, Equal Access Survey (EAS) consent, and HEA Deprivation Index Score (DIS) Eircode matching.

---

## 1. Summary Matrix: What This Data Can vs Cannot Show

| Analytical Question | Can Public HEA + Pobal Data Show This? | What AccessLens-IE Shows (`2019/2020` to `2025/2026`) | What Requires Internal MAP / HEA Microdata |
| :--- | :--- | :--- | :--- |
| **Institutional Enrolment Trajectory & Sector Benchmarking** | **YES** | Maynooth University grew **`+22.6%`** (`13,005` to `15,945`), outpacing IUA universities (`+17.7%`) and all `26` HEA institutions (`+15.1%`). | New entrant vs continuing student retention, progression from Year 1 to Year 2, and completion rates by entry route. |
| **Mature (`24+`) & Flexible / Part-Time Participation** | **YES (Aggregate)** | MU mature headcount held steady (`3,195` to `3,140`), while mature share shifted from `24.6%` to `19.7%` (`-4.9 pp`); flexible/part-time share is `10.4%` (`1,665` students). | Disadvantaged share *within* the mature cohort (NAP target: raising mature disadvantaged new entrants from `11%` to `20%`). |
| **Foundation, Access & Non-Honours Undergraduate Pathways** | **PARTIAL (Programme Level Only)** | Standalone SRS `Foundation and Access` rose `+31.0%` nationally (`790` to `1,035`; `20` at MU). Broader non-honours UG pathways at MU total `880` (`6.6%` of UG). | Direct-entry HEAR, DARE, QQI/FET entrants, and Turn to Teaching / foundation graduates who have progressed into Honours Degrees (`12,430` at MU). |
| **County-Level Socio-Economic Catchment & Participation** | **YES (Ecological / County Grain)** | Across `26` counties (`3,417` EDs, `5,149,139` population), county Pobal score correlates with HE participation per `1,000` ($r = 0.680$, 95% CI `0.397` to `0.845`, $p = 0.0001$). MU draws `4,775` (`32.4%`) of its Irish students from the `19` below-average counties. | Individual student Small Area / Eircode deprivation (HEA Deprivation Index Score) to measure whether students from affluent counties (e.g., Dublin `4,530`, Kildare `2,830`, Meath `1,785`) come from disadvantaged local communities. |
| **Disability (DARE) & Traveller / Roma Participation** | **NO (Not in Public SRS CSVs)** | Explicitly documented as unavailable in public `Access our Data - Students` exports (`KPI_01` to `KPI_06` dictionary notes). | Equal Access Survey (EAS) voluntary self-declarations, DARE admissions records, and Disability Office registration data (NAP disability target: `16%`). |
| **Causal Impact of Specific Access Interventions** | **NO** | Reports descriptive longitudinal trends, cross-institutional benchmarks, and ecological associations with 95% CIs. | Quasi-experimental evaluation (difference-in-differences, propensity score matching, survival analysis) on longitudinal student cohort microdata. |

---

## 2. Five Mandatory Analytical Limitations

### 2.1 County-Level (Ecological) Deprivation vs Student-Level Deprivation
* **What We Measure:** Step 3 links HEA Irish-domiciled enrolments by home county (`238,105` mapped students in `2025/2026`, after quarantining `145` `Unknown Ireland` / `N/A` records) to the population-weighted Pobal HP 2022 relative deprivation index across **`3,417`** Electoral Divisions in **`26`** counties.
* **Why Ecological Inference Must Not Be Overstated:** Every county contains both affluent and disadvantaged Electoral Divisions and Small Areas. For example, **Dublin** has a net affluent county-wide population-weighted score (**`+2.69`**), yet **`9.6%`** of Dublin's **`1,458,154`** residents live in Electoral Divisions classified as disadvantaged (`Index22_ED_rel_wt_cat` in categories `1` to `3`). Conversely, a student domiciled in a county with a negative mean Pobal score (such as **Longford** at **`-5.33`**, **Wexford** at **`-4.09`**, **Cavan** at **`-3.99`**, or **Offaly** at **`-3.95`**) may personally come from an affluent household.
* **Policy Implication:** County-level analysis is highly informative for **regional outreach planning, school-link geography, and commuter catchment monitoring**, whereas **NAP Goal 1 target tracking** (raising the disadvantaged-area transition rate from **`42%`** to **`54%`**) requires Small Area Eircode geocoding inside the institutional student record system.

### 2.2 Absence of Disability, Ethnicity, and Socio-Economic Entry Route Flags in Public SRS Exports
* The public HEA `Access our Data - Students` interactive download tool publishes aggregate headcount cross-tabulations across nine structural dimensions (`Institute`, `Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`, `Domicile Group`, `Gender`, and Irish-domiciled `County`).
* It does **not** include disability category, DARE/HEAR eligibility or offer acceptance, DEIS post-primary school attendance, QQI/FET entry basis, socio-economic group, or Irish Traveller and Roma ethnicity. Those variables are collected separately through the **HEA Equal Access Survey (EAS)** and institutional Access Office registrations.

### 2.3 Nearest-`5` Rounding and Small-Cell Suppression (`<10`)
* **Published Rounding:** All values in the HEA `Access our Data - Students` exports are independently rounded to the nearest **`5`**. When summing atomic cells across a dimension (`Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`), independent rounding creates minor additive differences up to **`15`** students compared with the published `Row_Total` (`890` institution-year-dimension tables reconcile within `10` students).
* **GDPR-Style Small-Cell Suppression Rule:** In accordance with statistical disclosure control practice under GDPR and HEA reporting standards, AccessLens-IE flags and suppresses all non-zero cells strictly below **`10`** (i.e., published cells equal to **`5`**) as **`"<10"`** in output display fields (`72` institution-dimension cells and `134` county-institution flow cells, totalling **`206`** suppressed cells across the 7-year series).

### 2.4 Institutional Scope & Structural Changes (`2019/2020` to `2025/2026`)
* The dataset covers the **`26`** HEA-funded higher education institutions reporting to the SRS. Private/independent higher education providers not funded by the HEA are outside the scope of these tables.
* **National College of Ireland (NCI)** entered the HEA SRS reporting dataset in `2023/2024`; its **`4`** prior academic years (`2019/2020` to `2022/2023`) appear as `0` in raw multi-year exports and are explicitly flagged with `in_hea_scope = FALSE` in `gold.fact_institution_year` so pre-2023/2024 institutional averages are not distorted.
* **St. Angela's College** integrated with **Atlantic Technological University (ATU)** during the period, with programme transfers reflected in the later years of the `2019/2020` to `2025/2026` series.

### 2.5 Observational Data Only (No Causal Claims)
* All statistical relationships reported in AccessLens-IE (including the county-level correlation between Pobal HP relative affluence/deprivation score and higher education participation per `1,000` residents, $r = 0.680$) are **descriptive and associative**. Higher county participation rates in counties such as **Galway (`54.9` per `1,000`)**, **Cork (`51.1` per `1,000`)**, **Sligo (`47.3` per `1,000`)**, and **Kildare (`52.0` per `1,000`)** reflect a combination of socio-economic composition, secondary school attainment (`EDHIGH22` correlation $r = 0.628$), age structure, and physical proximity to university and technological university campuses.
