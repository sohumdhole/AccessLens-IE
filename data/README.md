# Raw Data Directory (`data/raw/`)

Raw source files are excluded from GitHub version control via `.gitignore` and can be
re-downloaded programmatically or via the public web portals below.

## 1. Higher Education Authority (HEA) - Access our Data (Students)
- **Portal URL**: https://hea.ie/statistics/data-for-download-and-visualisations/access-our-data/access-our-data-students/
- **Embedded Shiny App**: https://highereducationauthority.shinyapps.io/Enrolments_2026/
- **Licence**: HEA Open Data / Re-Use of Public Sector Information Regulations.
- **Exports used (2019/2020 to 2025/2026)**:
  - Tab 1 (`Data by Academic Year`): `Institute`, `Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`, `Domicile Group`, `Gender`, and `County` (filtered to `Domicile Group = Ireland`).
  - Tab 2 (`Choose Your Own Data`, exported for each academic year from `2019/2020` to `2025/2026`): `Institute x Programme Type`, `Institute x Age Group`, `Institute x Mode of Study`, `Institute x Field of Study`, `Institute x Course Level`, and `County x Institute` (filtered to `Domicile Group = Ireland`).

## 2. Pobal HP Deprivation Index Scores 2022 (Electoral Division Level)
- **Dataset Page**: https://data.gov.ie/dataset/pobal-hp-deprivation-index-scores-2022
- **Direct CSV URL**: https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv
- **File**: `hp-deprivation-index-scores-2022.csv` (3,417 Electoral Divisions; Census 2022 population and Haase-Pratschke relative and absolute deprivation scores).
- **Licence**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).

## Verification
Every file's byte size, download timestamp, and SHA-256 checksum are verified during Step 1 and recorded in `outputs/audit/manifest.json`.
