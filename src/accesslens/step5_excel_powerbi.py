"""Step 5: Formula-driven Excel KPI pack (openpyxl: institution dropdown, SUMIFS,
INDEX-MATCH, conditional formatting, charts) and Power BI star-schema export (CSV & Parquet).
"""
from __future__ import annotations

import duckdb
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from .audit import Audit
from .config import (
    ACADEMIC_YEARS,
    FOCUS_INSTITUTION,
    IUA_UNIVERSITIES,
    OUT,
    RAG_THRESHOLDS,
    SMALL_CELL_THRESHOLD,
    WAREHOUSE,
)

F = "Arial"
H1 = Font(name=F, size=14, bold=True, color="003865")
H2 = Font(name=F, size=11, bold=True, color="003865")
B = Font(name=F, size=10, bold=True)
N = Font(name=F, size=10)
INPUT = Font(name=F, size=10, color="0000FF", bold=True)
WHITE = Font(name=F, size=10, color="FFFFFF", bold=True)
HEAD_FILL = PatternFill("solid", fgColor="003865")
IN_FILL = PatternFill("solid", fgColor="FFF9C4")
TILE_FILL = PatternFill("solid", fgColor="EEF4FC")
RED_F = PatternFill("solid", fgColor="F4C7C7")
AMB_F = PatternFill("solid", fgColor="FDE9B8")
GRN_F = PatternFill("solid", fgColor="CDEFCD")
THIN = Border(bottom=Side(style="thin", color="D0D0D0"))


def _hdr(ws, row: int, headers: list[str], col: int = 1):
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=col + i, value=h)
        c.font = WHITE
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _add_rag_cf(ws, cell_range: str):
    for label, fill in [("RED", RED_F), ("AMBER", AMB_F), ("GREEN", GRN_F)]:
        ws.conditional_formatting.add(
            cell_range,
            CellIsRule(operator="equal", formula=[f'"{label}"'], fill=fill),
        )


def build_excel_pack(panel: pd.DataFrame, county_df: pd.DataFrame, kpi_dict: pd.DataFrame) -> tuple[str, int]:
    excel_dir = OUT / "excel"
    excel_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = excel_dir / "AccessLens_IE_KPI_Pack.xlsx"

    wb = Workbook()

    # -------------------------------------------------------------------------
    # Sheet 1: About
    # -------------------------------------------------------------------------
    ab = wb.active
    ab.title = "About"
    about_lines = [
        ("AccessLens-IE: Widening Participation & Equity of Access KPI Pack", H1),
        ("Evidence-driven monitoring pack for Maynooth University (MAP) and HEA-funded institutions (2019/2020 to 2025/2026).", N),
        ("", N),
        ("How to use this workbook", B),
        ("1. On the Dashboard sheet, select an institution in cell C3 ('Maynooth University', 'ALL HEA', or any of the 26 HEA institutions).", N),
        ("2. Adjust the editable analytical RAG thresholds in cells C4:C9 (yellow cells). All KPI tiles, RAG flags, and tables recalculate automatically.", N),
        ("3. Explore University_Peers for 2025/2026 benchmarking across the 7 traditional universities (SUMIFS & INDEX-MATCH formulas).", N),
        ("4. Explore County_Deprivation for the 26-county Pobal HP 2022 deprivation vs HE participation profile and Maynooth catchment reach.", N),
        ("", N),
        ("Formatting & Governance Conventions", B),
        ("Blue bold text on yellow fill = editable user input / threshold. Black text = live Excel formula (SUMIFS / INDEX-MATCH / IF).", N),
        (f"Statistical Disclosure Control (GDPR-style practice): HEA rounds counts to nearest 5; non-zero cells under {SMALL_CELL_THRESHOLD} display as '<10' in suppressed views.", N),
        ("Ecological Scope Note: Pobal HP 2022 deprivation is linked at county level (26 counties, population-weighted from 3,417 EDs), not per individual student.", N),
        ("Sources: HEA 'Access our Data - Students' (2019/20-2025/26) & Pobal HP Deprivation Index 2022 (CC BY 4.0). Code: MIT Licence.", N),
    ]
    for idx, (txt, fnt) in enumerate(about_lines, 1):
        ab.cell(row=idx, column=1, value=txt).font = fnt
    ab.column_dimensions["A"].width = 125

    # -------------------------------------------------------------------------
    # Sheet 6 (created early for formula references): Institution_Year
    # -------------------------------------------------------------------------
    iy_ws = wb.create_sheet("Institution_Year")
    iy_cols = [
        "inst_year_key",
        "academic_year",
        "institute",
        "sector_group",
        "total_enrolments",
        "foundation_access_enrolments",
        "ug_access_pathway_enrolments",
        "honours_degree_enrolments",
        "mature_24plus_enrolments",
        "young_23under_enrolments",
        "part_time_enrolments",
        "other_mode_enrolments",
        "flexible_enrolments",
        "undergraduate_enrolments",
        "postgraduate_enrolments",
        "edu_soc_enrolments",
        "irish_county_mapped_enrolments",
        "deprived_county_enrolments",
    ]
    iy_headers = [
        "Key (Inst|Year)",
        "Academic Year",
        "Institute",
        "Sector Group",
        "Total Enrolments",
        "Foundation & Access",
        "UG Access & Cert Pathways",
        "Honours Degrees",
        "Mature (24+)",
        "Young (<=23)",
        "Part-Time",
        "Other Flexible Mode",
        "Total Flexible (PT+Other)",
        "Undergraduate",
        "Postgraduate",
        "Education & Social Sci",
        "Irish County-Mapped",
        "Deprived-County (<0) Enrolments",
    ]
    _hdr(iy_ws, 1, iy_headers)
    data_iy = panel.sort_values(["institute", "academic_year"]).reset_index(drop=True)
    for _, r in data_iy.iterrows():
        key_str = f"{r['institute']}|{r['academic_year']}"
        iy_ws.append(
            [
                key_str,
                r["academic_year"],
                r["institute"],
                r["sector_group"],
                int(r["total_enrolments"]),
                int(r["foundation_access_enrolments"]),
                int(r["ug_access_pathway_enrolments"]),
                int(r["honours_degree_enrolments"]),
                int(r["mature_24plus_enrolments"]),
                int(r["young_23under_enrolments"]),
                int(r["part_time_enrolments"]),
                int(r["other_mode_enrolments"]),
                int(r["flexible_enrolments"]),
                int(r["undergraduate_enrolments"]),
                int(r["postgraduate_enrolments"]),
                int(r["edu_soc_enrolments"]),
                int(r["irish_county_mapped_enrolments"]),
                int(r["deprived_county_enrolments"]),
            ]
        )
    last_iy = len(data_iy) + 1
    iy_ws.freeze_panes = "A2"
    iy_ws.auto_filter.ref = f"A1:R{last_iy}"
    for col_i in range(1, 19):
        iy_ws.column_dimensions[get_column_letter(col_i)].width = 22 if col_i <= 4 else 16

    R_IY = lambda c: f"Institution_Year!${c}$2:${c}${last_iy}"  # noqa: E731
    KEY_COL = R_IY("A")
    YR_COL = R_IY("B")
    INST_COL = R_IY("C")
    TOT_COL = R_IY("E")
    FA_COL = R_IY("F")
    PATH_COL = R_IY("G")
    MAT_COL = R_IY("I")
    FLX_COL = R_IY("M")
    UG_COL = R_IY("N")
    EDUSOC_COL = R_IY("P")
    IRMAP_COL = R_IY("Q")
    DEPCTY_COL = R_IY("R")

    # -------------------------------------------------------------------------
    # Sheet 2: Dashboard (inserted at position 1)
    # -------------------------------------------------------------------------
    db = wb.create_sheet("Dashboard", 1)
    db["A1"] = "AccessLens-IE: Widening Participation & National Access Plan KPI Dashboard"
    db["A1"].font = H1

    inputs = [
        ("Institution (dropdown)", FOCUS_INSTITUTION, "Select Maynooth University, ALL HEA, or any individual HEI"),
        ("Mature (24+) Share GREEN threshold (>=", RAG_THRESHOLDS["mature_share"]["green"], "Analytical RAG threshold for Mature (24+) share"),
        ("Mature (24+) Share AMBER threshold (>=", RAG_THRESHOLDS["mature_share"]["amber"], "Analytical RAG threshold for Mature (24+) share"),
        ("Flexible (PT+Other) Share GREEN threshold (>=", RAG_THRESHOLDS["flexible_share"]["green"], "Analytical RAG threshold for Flexible study share"),
        ("Flexible (PT+Other) Share AMBER threshold (>=", RAG_THRESHOLDS["flexible_share"]["amber"], "Analytical RAG threshold for Flexible study share"),
        ("Deprived-County (<0) Reach GREEN threshold (>=", RAG_THRESHOLDS["deprived_county_share"]["green"], "Analytical RAG threshold for share from counties with Pobal score < 0"),
        ("Deprived-County (<0) Reach AMBER threshold (>=", RAG_THRESHOLDS["deprived_county_share"]["amber"], "Analytical RAG threshold for share from counties with Pobal score < 0"),
    ]
    for idx, (lab, val, note) in enumerate(inputs, 3):
        db.cell(row=idx, column=1, value=lab).font = B
        c = db.cell(row=idx, column=3, value=val)
        c.font = INPUT
        c.fill = IN_FILL
        c.comment = Comment(note, "AccessLens-IE")
        if isinstance(val, float):
            c.number_format = "0.0%"

    # Dropdown list of institutions on Lookup column Z
    inst_list = ["ALL HEA", FOCUS_INSTITUTION] + sorted(
        i for i in data_iy["institute"].unique() if i != FOCUS_INSTITUTION
    )
    for i, inst_name in enumerate(inst_list, 1):
        db.cell(row=i, column=26, value=inst_name).font = Font(name=F, size=8, color="808080")
    dv = DataValidation(type="list", formula1=f"=$Z$1:$Z${len(inst_list)}", allow_blank=False)
    db.add_data_validation(dv)
    dv.add("C3")

    db["E3"] = "Active SUMIFS institution filter"
    db["E3"].font = Font(name=F, size=9, italic=True, color="666666")
    db["F3"] = '=IF($C$3="ALL HEA","*",$C$3)'

    SEL = "$F$3"
    MAT_G, MAT_A = "$C$4", "$C$5"
    FLX_G, FLX_A = "$C$6", "$C$7"
    DEP_G, DEP_A = "$C$8", "$C$9"

    # Headline KPI Tiles for Latest Year (2025/2026)
    db["A11"] = "Headline KPIs in 2025/2026 (Selected Institution / Sector)"
    db["A11"].font = H2
    _hdr(db, 12, ["KPI Metric (2025/2026)", "Value (Formula)", "RAG / Reference Note"])

    tiles = [
        (
            "Total Enrolments (2025/2026)",
            f'=SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")',
            "#,##0",
            '=IF($C$3="ALL HEA","Full HEA Sector",INDEX(Institution_Year!$D$2:$D$' + str(last_iy) + ',MATCH($C$3&"|2025/2026",' + KEY_COL + ',0)))',
        ),
        (
            "6-Year Enrolment Growth (2019/20 to 2025/26)",
            f'=(SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")-SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2019/2020"))/MAX(1,SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2019/2020"))',
            "+0.0%;-0.0%;0.0%",
            '"vs 2019/2020 baseline"',
        ),
        (
            "Mature Student Share (Age 24+, 2025/2026)",
            f'=SUMIFS({MAT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")/MAX(1,SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026"))',
            "0.0%",
            f'=IF(B15>={MAT_G},"GREEN",IF(B15>={MAT_A},"AMBER","RED"))',
        ),
        (
            "Part-Time & Flexible Share (2025/2026)",
            f'=SUMIFS({FLX_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")/MAX(1,SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026"))',
            "0.0%",
            f'=IF(B16>={FLX_G},"GREEN",IF(B16>={FLX_A},"AMBER","RED"))',
        ),
        (
            "UG Access & Non-Honours Pathway Share of UG (2025/2026)",
            f'=SUMIFS({PATH_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")/MAX(1,SUMIFS({UG_COL},{INST_COL},{SEL},{YR_COL},"2025/2026"))',
            "0.0%",
            '=IF(B17>=0.08,"GREEN",IF(B17>=0.05,"AMBER","RED"))',
        ),
        (
            "Disadvantaged-County Reach (Pobal < 0, 2025/2026)",
            f'=SUMIFS({DEPCTY_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")/MAX(1,SUMIFS({IRMAP_COL},{INST_COL},{SEL},{YR_COL},"2025/2026"))',
            "0.0%",
            f'=IF(B18>={DEP_G},"GREEN",IF(B18>={DEP_A},"AMBER","RED"))',
        ),
        (
            "Education & Social Sciences Share (2025/2026)",
            f'=SUMIFS({EDUSOC_COL},{INST_COL},{SEL},{YR_COL},"2025/2026")/MAX(1,SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},"2025/2026"))',
            "0.0%",
            '=IF(B19>=0.15,"GREEN",IF(B19>=0.10,"AMBER","RED"))',
        ),
    ]
    for idx, (label, fml, num_fmt, rag_fml) in enumerate(tiles, 13):
        db.cell(row=idx, column=1, value=label).font = N
        c_val = db.cell(row=idx, column=2, value=fml)
        c_val.font = B
        c_val.fill = TILE_FILL
        c_val.number_format = num_fmt
        c_rag = db.cell(row=idx, column=3, value=rag_fml)
        c_rag.font = B
        c_rag.alignment = Alignment(horizontal="center")

    _add_rag_cf(db, "C15:C19")

    # Multi-Year Trend Table (rows 22..29)
    top_yr = 22
    db.cell(row=top_yr - 1, column=1, value="Academic Year Trajectory (2019/2020 to 2025/2026, Selected Institution)").font = H2
    yr_headers = [
        "Academic Year",
        "Total Enrolments",
        "Undergraduate",
        "Foundation & Access",
        "UG Access & Cert Pathways",
        "UG Pathway Share %",
        "Mature (24+) Enrolments",
        "Mature (24+) Share %",
        "Mature RAG",
        "Flexible (PT+Other)",
        "Flexible Share %",
        "Flexible RAG",
        "Deprived-County (<0) Share %",
        "Deprived-County RAG",
    ]
    _hdr(db, top_yr, yr_headers)

    for i, yr in enumerate(ACADEMIC_YEARS):
        r = top_yr + 1 + i
        db.cell(row=r, column=1, value=yr).font = B
        db.cell(row=r, column=2, value=f"=SUMIFS({TOT_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=3, value=f"=SUMIFS({UG_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=4, value=f"=SUMIFS({FA_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=5, value=f"=SUMIFS({PATH_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=6, value=f"=E{r}/MAX(1,C{r})").number_format = "0.0%"
        db.cell(row=r, column=7, value=f"=SUMIFS({MAT_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=8, value=f"=G{r}/MAX(1,B{r})").number_format = "0.0%"
        db.cell(row=r, column=9, value=f'=IF(H{r}>={MAT_G},"GREEN",IF(H{r}>={MAT_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        db.cell(row=r, column=10, value=f"=SUMIFS({FLX_COL},{INST_COL},{SEL},{YR_COL},$A{r})").number_format = "#,##0"
        db.cell(row=r, column=11, value=f"=J{r}/MAX(1,B{r})").number_format = "0.0%"
        db.cell(row=r, column=12, value=f'=IF(K{r}>={FLX_G},"GREEN",IF(K{r}>={FLX_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        db.cell(row=r, column=13, value=f"=SUMIFS({DEPCTY_COL},{INST_COL},{SEL},{YR_COL},$A{r})/MAX(1,SUMIFS({IRMAP_COL},{INST_COL},{SEL},{YR_COL},$A{r}))").number_format = "0.0%"
        db.cell(row=r, column=14, value=f'=IF(M{r}>={DEP_G},"GREEN",IF(M{r}>={DEP_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        for c_i in range(1, 15):
            db.cell(row=r, column=c_i).border = THIN

    end_yr = top_yr + len(ACADEMIC_YEARS)
    _add_rag_cf(db, f"I{top_yr+1}:I{end_yr}")
    _add_rag_cf(db, f"L{top_yr+1}:L{end_yr}")
    _add_rag_cf(db, f"N{top_yr+1}:N{end_yr}")

    # Two charts on Dashboard
    ch1 = LineChart()
    ch1.title = "Total and Undergraduate Enrolments by Academic Year"
    ch1.y_axis.title = "Enrolments"
    ch1.x_axis.title = "Academic Year"
    ch1.add_data(Reference(db, min_col=2, max_col=3, min_row=top_yr, max_row=end_yr), titles_from_data=True)
    ch1.set_categories(Reference(db, min_col=1, min_row=top_yr + 1, max_row=end_yr))
    ch1.width, ch1.height = 14, 9
    db.add_chart(ch1, "A32")

    ch2 = BarChart()
    ch2.title = "Mature (24+) and Flexible Study Shares by Year"
    ch2.y_axis.title = "Share (%)"
    ch2.add_data(Reference(db, min_col=8, max_col=8, min_row=top_yr, max_row=end_yr), titles_from_data=True)
    ch2.add_data(Reference(db, min_col=11, max_col=11, min_row=top_yr, max_row=end_yr), titles_from_data=True)
    ch2.set_categories(Reference(db, min_col=1, min_row=top_yr + 1, max_row=end_yr))
    ch2.width, ch2.height = 14, 9
    db.add_chart(ch2, "H32")

    for i, w in enumerate([44, 18, 22, 16, 18, 16, 16, 16, 14, 16, 16, 14, 18, 16], 1):
        db.column_dimensions[get_column_letter(i)].width = w
    db.freeze_panes = "A23"

    # -------------------------------------------------------------------------
    # Sheet 3: University_Peers (7 IUA Universities + Sector Totals, 2025/2026)
    # -------------------------------------------------------------------------
    up = wb.create_sheet("University_Peers", 2)
    up["A1"] = "Traditional Universities (7 IUA) Widening Participation Benchmark (2025/2026)"
    up["A1"].font = H1
    up_headers = [
        "University",
        "2019/2020 Enrolments",
        "2025/2026 Enrolments",
        "6-Year Growth %",
        "Foundation & Access (2025/26)",
        "UG Access & Cert Pathways",
        "UG Pathway Share %",
        "Mature (24+) Share %",
        "Mature RAG",
        "Flexible (PT+Other) Share %",
        "Flexible RAG",
        "Deprived-County (<0) Share %",
        "Deprived-County RAG",
        "Edu & Social Sci Share %",
    ]
    _hdr(up, 3, up_headers)

    for idx, u_name in enumerate(IUA_UNIVERSITIES, 4):
        up.cell(row=idx, column=1, value=u_name).font = B if u_name == FOCUS_INSTITUTION else N
        # Use INDEX-MATCH on Institution_Year key column for exact lookup demonstration
        k19 = f'$A{idx}&"|2019/2020"'
        k25 = f'$A{idx}&"|2025/2026"'
        up.cell(row=idx, column=2, value=f"=INDEX({TOT_COL},MATCH({k19},{KEY_COL},0))").number_format = "#,##0"
        up.cell(row=idx, column=3, value=f"=INDEX({TOT_COL},MATCH({k25},{KEY_COL},0))").number_format = "#,##0"
        up.cell(row=idx, column=4, value=f"=(C{idx}-B{idx})/B{idx}").number_format = "+0.0%;-0.0%;0.0%"
        up.cell(row=idx, column=5, value=f"=INDEX({FA_COL},MATCH({k25},{KEY_COL},0))").number_format = "#,##0"
        up.cell(row=idx, column=6, value=f"=INDEX({PATH_COL},MATCH({k25},{KEY_COL},0))").number_format = "#,##0"
        up.cell(row=idx, column=7, value=f"=F{idx}/INDEX({UG_COL},MATCH({k25},{KEY_COL},0))").number_format = "0.0%"
        up.cell(row=idx, column=8, value=f"=INDEX({MAT_COL},MATCH({k25},{KEY_COL},0))/C{idx}").number_format = "0.0%"
        up.cell(row=idx, column=9, value=f'=IF(H{idx}>=Dashboard!{MAT_G},"GREEN",IF(H{idx}>=Dashboard!{MAT_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        up.cell(row=idx, column=10, value=f"=INDEX({FLX_COL},MATCH({k25},{KEY_COL},0))/C{idx}").number_format = "0.0%"
        up.cell(row=idx, column=11, value=f'=IF(J{idx}>=Dashboard!{FLX_G},"GREEN",IF(J{idx}>=Dashboard!{FLX_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        up.cell(row=idx, column=12, value=f"=INDEX({DEPCTY_COL},MATCH({k25},{KEY_COL},0))/INDEX({IRMAP_COL},MATCH({k25},{KEY_COL},0))").number_format = "0.0%"
        up.cell(row=idx, column=13, value=f'=IF(L{idx}>=Dashboard!{DEP_G},"GREEN",IF(L{idx}>=Dashboard!{DEP_A},"AMBER","RED"))').alignment = Alignment(horizontal="center")
        up.cell(row=idx, column=14, value=f"=INDEX({EDUSOC_COL},MATCH({k25},{KEY_COL},0))/C{idx}").number_format = "0.0%"

    end_u = 3 + len(IUA_UNIVERSITIES)
    tot_u_row = end_u + 1
    up.cell(row=tot_u_row, column=1, value="7 IUA Universities Pooled Total").font = B
    up.cell(row=tot_u_row, column=2, value=f"=SUM(B4:B{end_u})").number_format = "#,##0"
    up.cell(row=tot_u_row, column=3, value=f"=SUM(C4:C{end_u})").number_format = "#,##0"
    up.cell(row=tot_u_row, column=4, value=f"=(C{tot_u_row}-B{tot_u_row})/B{tot_u_row}").number_format = "+0.0%;-0.0%;0.0%"
    up.cell(row=tot_u_row, column=5, value=f"=SUM(E4:E{end_u})").number_format = "#,##0"
    up.cell(row=tot_u_row, column=6, value=f"=SUM(F4:F{end_u})").number_format = "#,##0"
    up.cell(row=tot_u_row, column=7, value=f"=AVERAGE(G4:G{end_u})").number_format = "0.0%"
    up.cell(row=tot_u_row, column=8, value=f"=AVERAGE(H4:H{end_u})").number_format = "0.0%"
    up.cell(row=tot_u_row, column=10, value=f"=AVERAGE(J4:J{end_u})").number_format = "0.0%"
    up.cell(row=tot_u_row, column=12, value=f"=AVERAGE(L4:L{end_u})").number_format = "0.0%"
    up.cell(row=tot_u_row, column=14, value=f"=AVERAGE(N4:N{end_u})").number_format = "0.0%"
    _add_rag_cf(up, f"I4:I{end_u}")
    _add_rag_cf(up, f"K4:K{end_u}")
    _add_rag_cf(up, f"M4:M{end_u}")
    up.conditional_formatting.add(
        f"L4:L{end_u}",
        ColorScaleRule(start_type="min", start_color="FDE9B8", end_type="max", end_color="CDEFCD"),
    )

    ch_u = BarChart()
    ch_u.title = "Disadvantaged-County Reach (<0 Pobal Score) Across Traditional Universities (2025/2026)"
    ch_u.y_axis.title = "Share of Irish County-Mapped Enrolments (%)"
    ch_u.add_data(Reference(up, min_col=12, max_col=12, min_row=3, max_row=end_u), titles_from_data=True)
    ch_u.set_categories(Reference(up, min_col=1, min_row=4, max_row=end_u))
    ch_u.width, ch_u.height = 16, 9
    up.add_chart(ch_u, "A13")

    for i in range(1, 15):
        up.column_dimensions[get_column_letter(i)].width = 28 if i == 1 else 16

    # -------------------------------------------------------------------------
    # Sheet 4: County_Deprivation (26 Counties, Pobal 2022 + HEA 2025/2026)
    # -------------------------------------------------------------------------
    cd_ws = wb.create_sheet("County_Deprivation", 3)
    cd_ws["A1"] = "County-Level (Ecological) Pobal HP Deprivation 2022 vs Higher Education Enrolments (2025/2026)"
    cd_ws["A1"].font = H1
    cd_headers = [
        "County",
        "Census 2022 Population",
        "Pop-Weighted Pobal Relative Score",
        "Disadvantaged ED Pop Share %",
        "HEA Irish-Domiciled Enrolments (2025/26)",
        "HE Enrolments per 1,000 Pop (Formula)",
        "Maynooth Enrolments (2025/26)",
        "Maynooth Share of County HE % (Formula)",
        "Maynooth Share of MU Total % (Formula)",
        "County Deprivation Band",
    ]
    _hdr(cd_ws, 3, cd_headers)

    cty_sorted = county_df.sort_values("pop_wt_rel_deprivation", ascending=True).reset_index(drop=True)
    start_c = 4
    end_c = start_c + len(cty_sorted) - 1
    for i, r in cty_sorted.iterrows():
        row_n = start_c + i
        cd_ws.cell(row=row_n, column=1, value=r["county"]).font = B
        cd_ws.cell(row=row_n, column=2, value=int(round(r["pop_2022"]))).number_format = "#,##0"
        cd_ws.cell(row=row_n, column=3, value=round(float(r["pop_wt_rel_deprivation"]), 3)).number_format = "+0.00;-0.00;0.00"
        cd_ws.cell(row=row_n, column=4, value=round(float(r["disadvantaged_pop_share"]), 4)).number_format = "0.0%"
        cd_ws.cell(row=row_n, column=5, value=int(r["hea_enrol_2025_2026"])).number_format = "#,##0"
        cd_ws.cell(row=row_n, column=6, value=f"=E{row_n}/(B{row_n}/1000)").number_format = "0.0"
        cd_ws.cell(row=row_n, column=7, value=int(r["mu_enrol_2025_2026"])).number_format = "#,##0"
        cd_ws.cell(row=row_n, column=8, value=f"=G{row_n}/E{row_n}").number_format = "0.0%"
        cd_ws.cell(row=row_n, column=9, value=f"=G{row_n}/SUM($G${start_c}:$G${end_c})").number_format = "0.0%"
        cd_ws.cell(row=row_n, column=10, value=f'=IF(C{row_n}<0,"Below National Mean (<0)","Above National Mean (>=0)")')

    cd_ws.conditional_formatting.add(
        f"F{start_c}:F{end_c}",
        ColorScaleRule(start_type="min", start_color="F4C7C7", end_type="max", end_color="CDEFCD"),
    )

    ch_c = BarChart()
    ch_c.title = "HE Enrolments per 1,000 Residents (Ordered from Most Disadvantaged to Most Affluent County)"
    ch_c.y_axis.title = "Enrolments per 1,000 Pop"
    ch_c.add_data(Reference(cd_ws, min_col=6, max_col=6, min_row=3, max_row=end_c), titles_from_data=True)
    ch_c.set_categories(Reference(cd_ws, min_col=1, min_row=start_c, max_row=end_c))
    ch_c.width, ch_c.height = 18, 9
    cd_ws.add_chart(ch_c, "A32")

    for i in range(1, 11):
        cd_ws.column_dimensions[get_column_letter(i)].width = 24 if i in (1, 10) else 18

    # -------------------------------------------------------------------------
    # Sheet 5: KPI_Dictionary
    # -------------------------------------------------------------------------
    kd_ws = wb.create_sheet("KPI_Dictionary", 4)
    kd_ws["A1"] = "National Access Plan (2022-2028) KPI Dictionary & Governance Mapping"
    kd_ws["A1"].font = H1
    _hdr(kd_ws, 3, list(kpi_dict.columns))
    for _, r in kpi_dict.iterrows():
        kd_ws.append(list(r.values))
    for i in range(1, len(kpi_dict.columns) + 1):
        kd_ws.column_dimensions[get_column_letter(i)].width = 28

    wb.save(xlsx_path)

    n_formulas = sum(
        1
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for c in row
        if isinstance(c.value, str) and c.value.startswith("=")
    )
    return str(xlsx_path), n_formulas


def build_powerbi_exports() -> dict:
    pbi_dir = OUT / "powerbi"
    pbi_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    fact_iy = con.execute("SELECT * FROM gold.fact_institution_year ORDER BY academic_year, institute").df()
    fact_dim = con.execute("SELECT * FROM gold.fact_institution_dimension_year ORDER BY academic_year, institute, dimension_type, category").df()
    fact_cty = con.execute("SELECT * FROM gold.fact_county_deprivation ORDER BY county").df()
    con.close()

    panel_df = pd.read_csv(OUT / "kpis" / "institution_access_kpis_by_year.csv")[
        [
            "institute",
            "academic_year",
            "irish_county_mapped_enrolments",
            "deprived_county_enrolments",
            "deprived_county_share",
        ]
    ]
    rag_df = pd.read_csv(OUT / "kpis" / "nap_rag_monitoring.csv")
    rag_inst = rag_df[rag_df["entity_type"] == "Institution"][
        [
            "institute",
            "academic_year",
            "rag_mature_share",
            "rag_flexible_share",
            "rag_ug_pathway_breadth",
            "rag_deprived_county_reach",
            "rag_edu_soc_share",
            "overall_rag_summary",
        ]
    ]

    # 1. dim_institution
    insts = (
        fact_iy[["institute", "combined_institute", "sector_group", "is_iua_university", "is_maynooth"]]
        .drop_duplicates()
        .sort_values("institute")
        .reset_index(drop=True)
    )
    insts.insert(0, "institution_key", range(1, len(insts) + 1))
    inst_key_map = dict(zip(insts["institute"], insts["institution_key"]))

    # 2. dim_academic_year
    dim_yr = pd.DataFrame(
        {
            "year_key": range(1, len(ACADEMIC_YEARS) + 1),
            "academic_year": ACADEMIC_YEARS,
            "start_year": [int(y[:4]) for y in ACADEMIC_YEARS],
            "end_year": [int(y[5:]) for y in ACADEMIC_YEARS],
            "nap_period": [
                "Pre-NAP 2022-2028 Baseline" if int(y[:4]) < 2022 else "NAP 2022-2028 Active Period"
                for y in ACADEMIC_YEARS
            ],
        }
    )
    yr_key_map = dict(zip(dim_yr["academic_year"], dim_yr["year_key"]))

    # 3. dim_county
    dim_cty = fact_cty[
        [
            "county",
            "province",
            "cso_ed_prefixes",
            "n_electoral_divisions",
            "pop_2022",
            "pop_wt_rel_deprivation",
            "pop_wt_abs_deprivation",
            "disadvantaged_ed_count",
            "disadvantaged_pop_2022",
            "disadvantaged_pop_share",
            "pop_wt_edhigh22_pct",
            "pop_wt_edlow22_pct",
            "is_below_national_affluence",
        ]
    ].copy()
    dim_cty.insert(0, "county_key", range(1, len(dim_cty) + 1))
    dim_cty["deprivation_band"] = dim_cty["is_below_national_affluence"].map(
        {True: "Below National Mean (<0)", False: "Above National Mean (>=0)"}
    )
    cty_key_map = dict(zip(dim_cty["county"], dim_cty["county_key"]))

    # 4. dim_rag
    dim_rag = pd.DataFrame(
        {
            "rag_status": ["GREEN", "AMBER", "RED", "NOT SCORED"],
            "rag_order": [1, 2, 3, 4],
            "rag_hex": ["#1B5E20", "#E65100", "#B71C1C", "#757575"],
        }
    )

    # 5. fact_institution_year
    f_iy = fact_iy.merge(panel_df, on=["institute", "academic_year"], how="left").merge(
        rag_inst, on=["institute", "academic_year"], how="left"
    )
    f_iy.insert(0, "institution_key", f_iy["institute"].map(inst_key_map))
    f_iy.insert(1, "year_key", f_iy["academic_year"].map(yr_key_map))
    f_iy["overall_rag_summary"] = f_iy["overall_rag_summary"].fillna("NOT SCORED")

    # 6. fact_institution_dimension_year
    f_dim = fact_dim.copy()
    f_dim.insert(0, "institution_key", f_dim["institute"].map(inst_key_map))
    f_dim.insert(1, "year_key", f_dim["academic_year"].map(yr_key_map))

    # 7. fact_county_year (26 counties x 7 years = 182 rows)
    cty_yr_rows = []
    for _, r in fact_cty.iterrows():
        c_name = r["county"]
        for yr in ACADEMIC_YEARS:
            ys = yr.replace("/", "_")
            cty_yr_rows.append(
                {
                    "county_key": cty_key_map[c_name],
                    "year_key": yr_key_map[yr],
                    "county": c_name,
                    "academic_year": yr,
                    "pop_2022": float(r["pop_2022"]),
                    "pop_wt_rel_deprivation": float(r["pop_wt_rel_deprivation"]),
                    "hea_irish_enrolments": int(r[f"hea_enrol_{ys}"]),
                    "enrol_per_1k_pop": float(r[f"enrol_per_1k_pop_{ys}"]),
                    "maynooth_irish_enrolments": int(r[f"mu_enrol_{ys}"]),
                    "maynooth_share_of_county": float(r[f"mu_share_of_county_{ys}"]),
                }
            )
    f_cty_yr = pd.DataFrame(cty_yr_rows)

    tables = {
        "dim_institution": insts,
        "dim_academic_year": dim_yr,
        "dim_county": dim_cty,
        "dim_rag": dim_rag,
        "fact_institution_year": f_iy,
        "fact_institution_dimension_year": f_dim,
        "fact_county_year": f_cty_yr,
    }
    for name, df in tables.items():
        df.to_csv(pbi_dir / f"{name}.csv", index=False)
        df.to_parquet(pbi_dir / f"{name}.parquet", index=False)

    return {k: len(v) for k, v in tables.items()}


def run() -> dict:
    a = Audit("step5_excel_powerbi")
    panel = pd.read_csv(OUT / "kpis" / "institution_access_kpis_by_year.csv")
    county_df = pd.read_csv(OUT / "geography" / "county_deprivation_enrolments.csv")
    kpi_dict = pd.read_csv(OUT / "kpis" / "kpi_dictionary.csv")

    xlsx_path, n_formulas = build_excel_pack(panel, county_df, kpi_dict)
    pbi_counts = build_powerbi_exports()

    a.put("excel_formula_count", n_formulas, "int", "outputs/excel/AccessLens_IE_KPI_Pack.xlsx")
    a.put("excel_sheet_count", 6, "plain_int", "outputs/excel/AccessLens_IE_KPI_Pack.xlsx")
    a.put("pbi_fact_inst_year_rows", pbi_counts["fact_institution_year"], "int", "outputs/powerbi/fact_institution_year.csv")
    a.put("pbi_fact_inst_dim_rows", pbi_counts["fact_institution_dimension_year"], "int", "outputs/powerbi/fact_institution_dimension_year.csv")
    a.put("pbi_fact_county_year_rows", pbi_counts["fact_county_year"], "int", "outputs/powerbi/fact_county_year.csv")
    a.put("pbi_dim_institution_rows", pbi_counts["dim_institution"], "plain_int", "outputs/powerbi/dim_institution.csv")
    a.put("pbi_dim_county_rows", pbi_counts["dim_county"], "plain_int", "outputs/powerbi/dim_county.csv")
    a.put("pbi_dim_year_rows", pbi_counts["dim_academic_year"], "plain_int", "outputs/powerbi/dim_academic_year.csv")

    artefacts = ["outputs/excel/AccessLens_IE_KPI_Pack.xlsx"]
    for tname in pbi_counts:
        artefacts.append(f"outputs/powerbi/{tname}.csv")
        artefacts.append(f"outputs/powerbi/{tname}.parquet")
    a.save(artefacts)
    return {"excel_path": xlsx_path, "n_formulas": n_formulas, "pbi_counts": pbi_counts}
