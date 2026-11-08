"""Build a clean, GitHub-ready release copy and zip archive of AccessLens-IE.

Excludes:
  - data/raw/* (except data/raw/.gitkeep)
  - warehouse/ and any *.duckdb files
  - __pycache__, .pytest_cache, .venv, *.pyc
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "warehouse",
    "dist",
    "build",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".duckdb",
    ".duckdb.wal",
}


def should_include(rel_path: Path) -> bool:
    """Return True if a relative path belongs in the clean GitHub release copy."""
    parts = rel_path.parts
    if any(p in EXCLUDED_DIRS for p in parts):
        return False
    if rel_path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if len(parts) >= 2 and parts[0] == "data" and parts[1] == "raw":
        return rel_path.name == ".gitkeep"
    return True


def list_release_files(root: Path = REPO_ROOT) -> List[Path]:
    """Return sorted relative paths of all files included in the GitHub-ready copy."""
    included: List[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root)
            if should_include(rel):
                included.append(rel)
    return included


def build_clean_copy(dest_dir: Path, root: Path = REPO_ROOT) -> List[Path]:
    """Copy only GitHub-ready release files into dest_dir."""
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    files = list_release_files(root)
    for rel in files:
        src_path = root / rel
        dst_path = dest_dir / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
    return files


def build_zip_archive(zip_path: Path, source_dir: Path, include_all: bool = False) -> int:
    """Create a zip archive from source_dir."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(source_dir.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(source_dir)
            if not include_all and any(
                part in {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
                for part in rel.parts
            ):
                continue
            arcname = Path("AccessLens-IE") / rel
            zf.write(p, arcname=str(arcname))
            count += 1
    return count


if __name__ == "__main__":
    rel_files = list_release_files()
    print(f"GitHub-ready release file count: {len(rel_files)}")
