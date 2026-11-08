# Power BI Star-Schema Build Guide & Reconciliation Check Values

**Project:** AccessLens-IE  
**Author:** Sohum Vivek Dhole  
**Star Schema Export Folder:** `outputs/powerbi/` (both `.csv` and `.parquet` provided)  
**DAX Measures File:** [`outputs/powerbi/measures.dax`](../outputs/powerbi/measures.dax)

---

## 1. Star-Schema Data Model (`outputs/powerbi/`)

Import the seven tables from `outputs/powerbi/` (prefer `.parquet` for strict data types or `.csv` with UTF-8 encoding):

| Table Name | Role | Row Count | Primary / Foreign Key | Grain Description |
| :--- | :--- | ---: | :--- | :--- |
| **`dim_academic_year`** | Dimension | `7` | `academic_year_key` (`1` to `7`) | Academic years `2019/2020` to `2025/2026` (`is_latest_year = TRUE` on `2025/2026`). |
| **`dim_institution`** | Dimension | `26` | `institution_key` (`1` to `26`) | All `26` HEA-funded institutions with `sector_group` and `is_maynooth` flag. |
| **`dim_county`** | Dimension | `26` | `county_key` (`1` to `26`) | All `26` Republic of Ireland counties (`3,417` EDs, `5,149,139` Census 2022 population, population-weighted Pobal HP 2022 scores). |
| **`dim_rag`** | Dimension | `4` | `rag_status` | RAG status lookup (`GREEN`, `AMBER`, `RED`, `INFO`) with hex colour codes and sort order. |
| **`fact_institution_year`** | Fact | `182` | `academic_year_key`, `institution_key` | Institution-by-year access KPIs (`26` institutions x `7` years = `182` rows) and `2025/2026` NAP RAG statuses. |
| **`fact_institution_dimension_year`** | Fact | `5,874` | `academic_year_key`, `institution_key` | Atomic multi-dimensional breakdowns (`Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`) with `<10` suppression flag (`72` flagged cells). |
| **`fact_county_year`** | Fact | `182` | `academic_year_key`, `county_key` | County-by-year Irish-domiciled total enrolments, Maynooth University enrolments, and rates per `1,000` residents (`26` counties x `7` years = `182` rows). |

### Relationships (Model View)
1. `dim_academic_year[academic_year_key]` (`1`) -> (`*`) `fact_institution_year[academic_year_key]` (Single direction, active)
2. `dim_institution[institution_key]` (`1`) -> (`*`) `fact_institution_year[institution_key]` (Single direction, active)
3. `dim_rag[rag_status]` (`1`) -> (`*`) `fact_institution_year[overall_rag_status]` (Single direction, active)
4. `dim_academic_year[academic_year_key]` (`1`) -> (`*`) `fact_institution_dimension_year[academic_year_key]` (Single direction, active)
5. `dim_institution[institution_key]` (`1`) -> (`*`) `fact_institution_dimension_year[institution_key]` (Single direction, active)
6. `dim_academic_year[academic_year_key]` (`1`) -> (`*`) `fact_county_year[academic_year_key]` (Single direction, active)
7. `dim_county[county_key]` (`1`) -> (`*`) `fact_county_year[county_key]` (Single direction, active)

---

## 2. Page-by-Page Build Guide & Exact Reconciliation Check Values

Use the DAX measures in [`outputs/powerbi/measures.dax`](../outputs/powerbi/measures.dax) to populate the four report pages below. Verify every visual against the audited check values before publishing.

### Page 1: Executive Overview & Maynooth University Benchmark (`2019/2020` to `2025/2026`)
* **Slicers:** `dim_academic_year[academic_year]` (default `2025/2026`), `dim_institution[institute]` (default `Maynooth University`), `dim_institution[sector_group]`.
* **Top KPI Cards (Verify with `Maynooth University` and `2025/2026` selected):**
  * `[Total Enrolments]` = **`15,945`** (Sector total unselected = **`283,940`**; IUA Universities = **`157,495`**)
  * `[6-Year Enrolment Growth %]` = **`+22.6%`** (`+2,940` students from **`13,005`** in `2019/2020`; YoY = **`+2.5%`** from **`15,560`**)
  * `[Mature Student Share %]` = **`19.7%`** (**`3,140`** mature students vs **`30.7%`** IUA and **`34.8%`** All HEA)
  * `[Flexible & Part-Time Share %]` = **`10.4%`** (**`1,665`** part-time/flexible students vs **`15.3%`** IUA and **`21.8%`** All HEA)
  * `[Deprived-County Catchment Share %]` = **`32.4%`** (**`4,775`** of **`14,720`** county-mapped Irish students)
* **Visuals:**
  1. **Line Chart:** `dim_academic_year[academic_year]` on X-axis; `[Total Enrolments]`, `[Mature Share %]`, and `[Flexible Share %]` comparing `Maynooth University`, `IUA Universities`, and `All HEA Institutions`.
  2. **Clustered Bar Chart:** Peer university comparison on `dim_institution[institute]` filtered to `sector_group = "IUA University"`.

### Page 2: Access Pathways, Programme Type & Discipline Mix
* **Filter:** `fact_institution_dimension_year[dimension_type]` switcher (`Programme Type`, `Field of Study`, `Course Level`, `Age Group`, `Mode of Study`).
* **Reconciliation Check Values (`2025/2026`):**
  * National Standalone `Foundation and Access` (`Programme Type`): **`1,035`** (up **`+31.0%`** from **`790`** in `2019/2020`; led by ATU Donegal **`470`**, TU Dublin City **`155`**, TCD **`140`**, University of Galway **`90`**, MTU Kerry **`80`**; Maynooth University **`20`**).
  * Maynooth Broad Non-Honours UG Pathways (`[UG Access Pathway Enrolments]`): **`880`** (**`6.6%`** of MU's **`13,310`** undergraduates; **`5.5%`** of total enrolments).
  * Maynooth Honours Degrees: **`12,430`** (**`78.0%`** of total enrolments, up **`+28.7%`** from **`9,660`**).
  * Maynooth Field of Study Mix (`2025/2026`): Business, Administration & Law **`4,950`** (**`31.1%`**), Arts & Humanities **`3,700`** (**`23.2%`**), Natural Sciences, Mathematics & Statistics **`2,120`** (**`13.3%`**), Social Sciences, Journalism & Information **`1,765`** (**`11.1%`**), Education **`1,385`** (**`8.7%`**), Health & Welfare **`535`** (**`3.4%`**, up **`+143.2%`** from **`220`** in `2019/2020`).
  * Combined Education + Social Sciences + Health & Welfare at Maynooth: **`3,150`** (**`19.8%`** vs **`12.9%`** All HEA).

### Page 3: Geography, Pobal HP Deprivation & Maynooth Regional Catchment (`2025/2026`)
* **Scatter Visual (`dim_county` + `fact_county_year` filtered to `2025/2026`):**
  * **X-Axis:** `dim_county[pop_weighted_rel_score_2022]`
  * **Y-Axis:** `[County Enrolments per 1,000 Pop]`
  * **Bubble Size:** `dim_county[census_pop_2022]`
  * **Legend:** `dim_county[deprivation_tier]`
* **Reconciliation Check Values (`2025/2026`):**
  * Total Census 2022 Population across `26` counties (`3,417` EDs): **`5,149,139`**
  * National County-Mapped Irish-Domiciled Enrolments: **`238,105`** (**`46.2`** per `1,000` residents)
  * Ecological Correlation (County Pobal Score vs Enrolments per `1,000`): **Pearson $r = 0.680$** (95% CI **`0.397` to `0.845`**, $p = 0.0001$), **Spearman $\rho = 0.693$** (95% CI **`0.371` to `0.883`**), OLS slope **`1.32`** ($R^2 = 46.2%$).
  * Maynooth Top Commuter & Regional Counties (`2025/2026`):
    * **Dublin:** **`4,530`** MU students (`7.1%` of Dublin's **`63,490`** HE students; Pobal **`+2.69`**)
    * **Kildare:** **`2,830`** MU students (**`22.0%`** of Kildare's **`12,875`** HE students; Pobal **`+3.11`**)
    * **Meath:** **`1,785`** MU students (**`17.0%`** of Meath's **`10,470`** HE students; Pobal **`+1.56`**)
    * **Westmeath:** **`590`** MU students (**`12.1%`** of Westmeath's **`4,860`** HE students; Pobal **`-1.43`**)
    * **Wexford:** **`570`** MU students (**`8.4%`** of Wexford's **`6,785`** HE students; Pobal **`-4.09`**)
    * **Offaly:** **`415`** MU students (**`11.6%`** of Offaly's **`3,585`** HE students; Pobal **`-3.95`**)
    * **Cavan:** **`365`** MU students (**`11.8%`** of Cavan's **`3,100`** HE students; Pobal **`-3.99`**)
    * **Laois:** **`350`** MU students (**`8.8%`** of Laois's **`3,960`** HE students; Pobal **`-2.02`**)
    * **Longford:** **`245`** MU students (**`12.3%`** of Longford's **`1,995`** HE students; Pobal **`-5.33`**)
    * **Carlow:** **`240`** MU students (**`8.0%`** of Carlow's **`2,995`** HE students; Pobal **`-2.76`**)
    * **Leitrim:** **`145`** MU students (**`9.1%`** of Leitrim's **`1,585`** HE students; Pobal **`-2.41`**)
* **Mandatory Page Footer Note:** *"County deprivation is an ecological (population-weighted Electoral Division) indicator, not an individual student deprivation measure. Published HEA counts are rounded to the nearest 5, and cells below 10 are suppressed as <10."*

### Page 4: National Access Plan (NAP) 2022-2028 RAG Scorecard (`2025/2026`)
* **Matrix Visual:** Rows = `dim_institution[institute]` grouped by `sector_group`; Values = `[Mature Share %]`, `[Flexible Share %]`, `[UG Access Pathway Share %]`, `[Deprived-County Catchment Share %]`, `[Education & Social Care Share %]`, and `overall_rag_status` conditionally formatted via `dim_rag[hex_color]`.
* **Reconciliation Check Values (`2025/2026`):**
  * Sector Composite RAG Distribution across `26` institutions: **`20` GREEN**, **`4` AMBER**, **`2` RED**.
  * Maynooth University RAG Profile: Overall **`AMBER`** (**`1` GREEN**: Deprived-County Share `32.4%` >= `20.0%`; **`3` AMBER**: Mature Share `19.7%` vs `25.0%` target, Flexible Share `10.4%` vs `15.0%` target, UG Pathway Share `6.6%` vs `8.0%` target; **`0` RED**).
