"""Step 7 Tests: Repository hygiene, no em dashes, .gitignore rules, Excel formulas, and Power BI exports."""
from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.make_release import build_clean_copy, list_release_files


TEXT_EXTENSIONS = {
    ".md",
    ".tmpl",
    ".py",
    ".dax",
    ".json",
    ".csv",
    ".txt",
    ".ini",
    ".gitignore",
    ".gitattributes",
}


def test_no_em_or_en_dashes_anywhere(repo_root: Path) -> None:
    """Zero em dashes (U+2014) or en dashes (U+2013) in any project text file."""
    for rel in list_release_files(repo_root):
        p = repo_root / rel
        if p.suffix.lower() in TEXT_EXTENSIONS or p.name in {".gitignore", ".gitattributes", "LICENSE"}:
            txt = p.read_text(encoding="utf-8")
            assert "\u2014" not in txt, f"Em dash found in {rel}"
            assert "\u2013" not in txt, f"En dash found in {rel}"


def test_no_forbidden_project_mentions(repo_root: Path) -> None:
    """Ensure forbidden prior project name never appears anywhere in repository."""
    forbidden = "".join(chr(c) for c in [99, 97, 114, 101, 101, 114, 116, 119, 105, 110])
    for rel in list_release_files(repo_root):
        p = repo_root / rel
        if p.suffix.lower() in TEXT_EXTENSIONS or p.name in {".gitignore", ".gitattributes", "LICENSE"}:
            txt = p.read_text(encoding="utf-8").lower()
            assert forbidden not in txt, f"Forbidden string found in {rel}"


def test_gitignore_excludes_raw_data_and_duckdb(repo_root: Path) -> None:
    gi = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "data/raw/*" in gi
    assert "!data/raw/.gitkeep" in gi
    assert "warehouse/" in gi
    assert "*.duckdb" in gi


def test_release_file_list_excludes_raw_data_and_database(repo_root: Path) -> None:
    rel_files = [str(p).replace("\\", "/") for p in list_release_files(repo_root)]
    assert "data/raw/.gitkeep" in rel_files
    for rf in rel_files:
        if rf.startswith("data/raw/"):
            assert rf == "data/raw/.gitkeep", f"Raw data file leaked into release: {rf}"
        assert not rf.startswith("warehouse/"), f"Warehouse file leaked into release: {rf}"
        assert not rf.endswith(".duckdb"), f"DuckDB file leaked into release: {rf}"


def test_excel_pack_formulas_dropdown_cf_and_charts(repo_root: Path) -> None:
    xlsx_path = repo_root / "outputs" / "excel" / "AccessLens_IE_KPI_Pack.xlsx"
    assert xlsx_path.exists()
    wb = openpyxl.load_workbook(xlsx_path, data_only=False)
    assert len(wb.sheetnames) == 6

    formula_count = 0
    has_sumifs = False
    has_index_match = False
    for name in wb.sheetnames:
        ws = wb[name]
        for row in ws.iter_rows(values_only=True):
            for val in row:
                if isinstance(val, str) and val.startswith("="):
                    formula_count += 1
                    u = val.upper()
                    if "SUMIFS(" in u:
                        has_sumifs = True
                    if "INDEX(" in u and "MATCH(" in u:
                        has_index_match = True

    assert formula_count > 300, f"Expected >300 Excel formulas, found {formula_count}"
    assert has_sumifs is True
    assert has_index_match is True

    ws_exec = wb["Dashboard"]
    assert ws_exec["C3"].value == "Maynooth University"
    assert len(ws_exec.data_validations.dataValidation) >= 1
    assert len(ws_exec._charts) >= 2
    assert len(ws_exec.conditional_formatting) >= 1


def test_powerbi_star_schema_exports_and_dax(repo_root: Path) -> None:
    pbi_dir = repo_root / "outputs" / "powerbi"
    expected_tables = [
        "dim_academic_year",
        "dim_institution",
        "dim_county",
        "dim_rag",
        "fact_institution_year",
        "fact_institution_dimension_year",
        "fact_county_year",
    ]
    for t in expected_tables:
        assert (pbi_dir / f"{t}.csv").exists(), f"Missing {t}.csv"
        assert (pbi_dir / f"{t}.parquet").exists(), f"Missing {t}.parquet"

    dax_path = pbi_dir / "measures.dax"
    assert dax_path.exists()
    dax_txt = dax_path.read_text(encoding="utf-8")
    assert "Total Enrolments =" in dax_txt
    assert "Deprived-County Catchment Share % =" in dax_txt
    assert "Dimension Enrolments (GDPR Suppressed Display) =" in dax_txt


def test_build_clean_github_copy_contains_no_raw_or_db(
    repo_root: Path, tmp_path: Path
) -> None:
    clean_dir = tmp_path / "AccessLens-IE-clean"
    copied = build_clean_copy(clean_dir, repo_root)
    assert len(copied) >= 45
    assert (clean_dir / "data" / "raw" / ".gitkeep").exists()
    raw_items = [p.name for p in (clean_dir / "data" / "raw").iterdir()]
    assert raw_items == [".gitkeep"]
    assert not (clean_dir / "warehouse").exists()
    assert not list(clean_dir.rglob("*.duckdb"))
    assert (clean_dir / "README.md").exists()
    assert (clean_dir / "outputs" / "audit" / "audit.json").exists()
    assert (clean_dir / "outputs" / "excel" / "AccessLens_IE_KPI_Pack.xlsx").exists()

