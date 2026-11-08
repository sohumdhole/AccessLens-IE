"""Central configuration, constants, county mappings, and National Access Plan reference settings."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
WAREHOUSE_DIR = ROOT / "warehouse"
WAREHOUSE = WAREHOUSE_DIR / "accesslens.duckdb"
DB_PATH = WAREHOUSE
OUT = ROOT / "outputs"
AUDIT_DIR = OUT / "audit"
AUDIT_PATH = AUDIT_DIR / "audit.json"
MANIFEST_PATH = AUDIT_DIR / "manifest.json"
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"

FOCUS_INSTITUTION = "Maynooth University"

ACADEMIC_YEARS = [
    "2019/2020",
    "2020/2021",
    "2021/2022",
    "2022/2023",
    "2023/2024",
    "2024/2025",
    "2025/2026",
]

# Traditional Universities (IUA members) used as Maynooth University's primary university peer group
IUA_UNIVERSITIES = [
    "Dublin City University",
    "Maynooth University",
    "Trinity College Dublin",
    "University College Cork",
    "University College Dublin",
    "University of Galway",
    "University of Limerick",
]

# Sector classification of all 26 HEA-funded institutions in the Student Record System (SRS) exports
INSTITUTION_SECTOR_MAP = {
    "Dublin City University": "Traditional University",
    "Maynooth University": "Traditional University",
    "Trinity College Dublin": "Traditional University",
    "University College Cork": "Traditional University",
    "University College Dublin": "Traditional University",
    "University of Galway": "Traditional University",
    "University of Limerick": "Traditional University",
    "ATU Donegal": "Technological University / IoT",
    "ATU Galway-Mayo": "Technological University / IoT",
    "ATU Sligo": "Technological University / IoT",
    "MTU Cork": "Technological University / IoT",
    "MTU Kerry": "Technological University / IoT",
    "SETU Carlow": "Technological University / IoT",
    "SETU Waterford": "Technological University / IoT",
    "TU Dublin Blanchardstown": "Technological University / IoT",
    "TU Dublin City": "Technological University / IoT",
    "TU Dublin Tallaght": "Technological University / IoT",
    "TUS Athlone": "Technological University / IoT",
    "TUS Limerick": "Technological University / IoT",
    "Dundalk IT": "Technological University / IoT",
    "Dun Laoghaire Institute of Art, Design and Technology": "Technological University / IoT",
    "Mary Immaculate College, Limerick": "Specialist / Other College",
    "National College of Art and Design": "Specialist / Other College",
    "National College of Ireland": "Specialist / Other College",
    "Royal College of Surgeons": "Specialist / Other College",
    "St. Angelas College of Home Economics, Sligo": "Specialist / Other College",
}

# Documented mapping from CSO 6-character Electoral Division code 2-digit prefixes in Pobal 2022
# to the 26 counties of the Republic of Ireland reported in HEA student data.
# Note: prefix '04' is Cork County/City and prefix '47' covers the 11 Cork City 2019 boundary extension EDs.
CSO_ED_PREFIX_TO_COUNTY = {
    "01": ("Carlow", "Leinster", "CSO ED prefix 01 -> Co. Carlow (54 EDs)"),
    "02": ("Cavan", "Ulster (ROI)", "CSO ED prefix 02 -> Co. Cavan (89 EDs)"),
    "03": ("Clare", "Munster", "CSO ED prefix 03 -> Co. Clare (151 EDs)"),
    "04": ("Cork", "Munster", "CSO ED prefix 04 -> Co. Cork & Cork City (399 EDs; combined with prefix 47)"),
    "47": ("Cork", "Munster", "CSO ED prefix 47 -> Cork City 2019 boundary extension EDs (11 EDs; combined with prefix 04)"),
    "05": ("Donegal", "Ulster (ROI)", "CSO ED prefix 05 -> Co. Donegal (149 EDs)"),
    "06": ("Galway", "Connacht", "CSO ED prefix 06 -> Co. Galway & Galway City (234 EDs)"),
    "07": ("Kerry", "Munster", "CSO ED prefix 07 -> Co. Kerry (164 EDs)"),
    "08": ("Kildare", "Leinster", "CSO ED prefix 08 -> Co. Kildare (89 EDs; Maynooth host county)"),
    "09": ("Kilkenny", "Leinster", "CSO ED prefix 09 -> Co. Kilkenny (113 EDs)"),
    "10": ("Laois", "Leinster", "CSO ED prefix 10 -> Co. Laois (97 EDs)"),
    "11": ("Leitrim", "Connacht", "CSO ED prefix 11 -> Co. Leitrim (72 EDs)"),
    "12": ("Limerick", "Munster", "CSO ED prefix 12 -> Co. Limerick & Limerick City (172 EDs)"),
    "13": ("Longford", "Leinster", "CSO ED prefix 13 -> Co. Longford (54 EDs)"),
    "14": ("Louth", "Leinster", "CSO ED prefix 14 -> Co. Louth (43 EDs)"),
    "15": ("Mayo", "Connacht", "CSO ED prefix 15 -> Co. Mayo (151 EDs)"),
    "16": ("Meath", "Leinster", "CSO ED prefix 16 -> Co. Meath (92 EDs)"),
    "17": ("Monaghan", "Ulster (ROI)", "CSO ED prefix 17 -> Co. Monaghan (70 EDs)"),
    "18": ("Offaly", "Leinster", "CSO ED prefix 18 -> Co. Offaly (86 EDs)"),
    "19": ("Roscommon", "Connacht", "CSO ED prefix 19 -> Co. Roscommon (109 EDs)"),
    "20": ("Sligo", "Connacht", "CSO ED prefix 20 -> Co. Sligo (80 EDs)"),
    "21": ("Tipperary", "Munster", "CSO ED prefix 21 -> Co. Tipperary North & South (175 EDs)"),
    "22": ("Waterford", "Munster", "CSO ED prefix 22 -> Co. Waterford & Waterford City (129 EDs)"),
    "23": ("Westmeath", "Leinster", "CSO ED prefix 23 -> Co. Westmeath (106 EDs)"),
    "24": ("Wexford", "Leinster", "CSO ED prefix 24 -> Co. Wexford (124 EDs)"),
    "25": ("Wicklow", "Leinster", "CSO ED prefix 25 -> Co. Wicklow (82 EDs)"),
    "26": ("Dublin", "Leinster", "CSO ED prefix 26 -> Co. Dublin (Dublin City, Dun Laoghaire-Rathdown, Fingal, South Dublin; 322 EDs)"),
}

# Small-cell statistical disclosure control (GDPR-style practice):
# HEA already rounds published counts to the nearest 5 (0, 5, 10, 15, ...).
# In public reporting tables, non-zero cells under 10 (i.e. 5) are suppressed as '<10'.
HEA_ROUNDING_BASE = 5
SMALL_CELL_THRESHOLD = 10

# National Access Plan 2022-2028 published national targets (source: HEA, 31 August 2022)
NAP_2022_2028_TARGETS = {
    "disadvantaged_area_transition_rate_baseline": 0.42,
    "disadvantaged_area_transition_rate_target": 0.54,
    "mature_disadvantaged_entrant_baseline": 0.11,
    "mature_disadvantaged_entrant_target": 0.20,
    "students_with_disabilities_new_entrant_target": 0.16,
    "students_with_disabilities_new_entrant_baseline": 0.124,
    "traveller_new_entrants_baseline": 33,
    "traveller_new_entrants_target": 150,
}

# Analytical RAG monitoring thresholds for institutional public SRS proxy KPIs
# (Explicitly distinguished from national new-entrant NAP targets)
RAG_THRESHOLDS = {
    "mature_share": {"green": 0.25, "amber": 0.18},           # Mature (24+) share of total enrolments
    "flexible_share": {"green": 0.15, "amber": 0.10},         # Part-time + Other share of total enrolments
    "ug_access_pathway_share": {"green": 0.08, "amber": 0.05}, # Non-honours degree & foundation share of UG enrolments
    "deprived_county_share": {"green": 0.20, "amber": 0.14},  # Share of Irish students from counties with Pobal score < 0
}

HEA_SOURCE_URL = "https://hea.ie/statistics/data-for-download-and-visualisations/access-our-data/access-our-data-students/"
HEA_SHINY_URL = "https://highereducationauthority.shinyapps.io/Enrolments_2026/"
POBAL_SOURCE_URL = "https://data.gov.ie/dataset/pobal-hp-deprivation-index-scores-2022"
POBAL_CSV_URL = "https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv"
NAP_LAUNCH_URL = "https://hea.ie/2022/08/31/minister-harris-launches-the-new-national-access-plan-to-drive-equality-of-access-to-higher-education/"
