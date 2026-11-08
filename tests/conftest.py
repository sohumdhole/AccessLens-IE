"""Pytest fixtures and path setup for AccessLens-IE."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def audit_payload(repo_root: Path) -> Dict:
    audit_path = repo_root / "outputs" / "audit" / "audit.json"
    assert audit_path.exists(), f"Missing audit.json at {audit_path}"
    return json.loads(audit_path.read_text(encoding="utf-8"))
