"""Step 6: Render README, methodology, scope/limitations guide, plain-English briefing,
Power BI build guide, and DAX measures from templates and the single audit record (`audit.json`).
"""
from __future__ import annotations

import json
import re

from .audit import load_metrics
from .config import (
    AUDIT_PATH,
    HEA_SHINY_URL,
    HEA_SOURCE_URL,
    POBAL_CSV_URL,
    POBAL_SOURCE_URL,
    ROOT,
    TEMPLATES,
)

PH = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
FORBIDDEN = ["\u2014", "\u2013"]  # em dash, en dash

TARGETS = {
    "README.md.tmpl": "README.md",
    "methodology.md.tmpl": "docs/methodology.md",
    "what_this_data_can_and_cannot_show.md.tmpl": "docs/what_this_data_can_and_cannot_show.md",
    "briefing_summary.md.tmpl": "docs/briefing_summary.md",
    "powerbi_build_guide.md.tmpl": "docs/powerbi_build_guide.md",
    "measures.dax.tmpl": "outputs/powerbi/measures.dax",
}
RENDER_TARGETS = list(TARGETS.items())


def render_text(template: str, metrics: dict) -> tuple[str, list[str]]:
    used = []

    def sub(m):
        k = m.group(1)
        if k not in metrics:
            raise KeyError(f"Template references unknown audit key: {k}")
        used.append(k)
        return str(metrics[k]["display"])

    return PH.sub(sub, template), used


def data_readme() -> str:
    lines = [
        "# Raw Data Directory (`data/raw/`)",
        "",
        "Raw source files are excluded from GitHub version control via `.gitignore` and can be",
        "re-downloaded programmatically or via the public web portals below.",
        "",
        "## 1. Higher Education Authority (HEA) - Access our Data (Students)",
        f"- **Portal URL**: {HEA_SOURCE_URL}",
        f"- **Embedded Shiny App**: {HEA_SHINY_URL}",
        "- **Licence**: HEA Open Data / Re-Use of Public Sector Information Regulations.",
        "- **Exports used (2019/2020 to 2025/2026)**:",
        "  - Tab 1 (`Data by Academic Year`): `Institute`, `Programme Type`, `Age Group`, `Mode of Study`, `Field of Study`, `Course Level`, `Domicile Group`, `Gender`, and `County` (filtered to `Domicile Group = Ireland`).",
        "  - Tab 2 (`Choose Your Own Data`, exported for each academic year from `2019/2020` to `2025/2026`): `Institute x Programme Type`, `Institute x Age Group`, `Institute x Mode of Study`, `Institute x Field of Study`, `Institute x Course Level`, and `County x Institute` (filtered to `Domicile Group = Ireland`).",
        "",
        "## 2. Pobal HP Deprivation Index Scores 2022 (Electoral Division Level)",
        f"- **Dataset Page**: {POBAL_SOURCE_URL}",
        f"- **Direct CSV URL**: {POBAL_CSV_URL}",
        "- **File**: `hp-deprivation-index-scores-2022.csv` (3,417 Electoral Divisions; Census 2022 population and Haase-Pratschke relative and absolute deprivation scores).",
        "- **Licence**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).",
        "",
        "## Verification",
        "Every file's byte size, download timestamp, and SHA-256 checksum are verified during Step 1 and recorded in `outputs/audit/manifest.json`.",
    ]
    return "\n".join(lines) + "\n"


def verify(metrics: dict | None = None) -> list[str]:
    """Return the documents whose committed text differs from a fresh render."""
    metrics = metrics or load_metrics()
    stale = []
    for src, dst in TARGETS.items():
        expected, _ = render_text((TEMPLATES / src).read_text(encoding="utf-8"), metrics)
        target_path = ROOT / dst
        if not target_path.exists() or target_path.read_text(encoding="utf-8") != expected:
            stale.append(dst)
    return stale


def verify_docs_match_audit(metrics: dict | None = None) -> bool:
    """Return True if all rendered documents match fresh renders from audit.json."""
    return len(verify(metrics)) == 0


def run(metrics: dict | None = None) -> dict:
    metrics = metrics or load_metrics()
    trace = {}
    for src, dst in TARGETS.items():
        text, used = render_text((TEMPLATES / src).read_text(encoding="utf-8"), metrics)
        for ch in FORBIDDEN:
            if ch in text:
                raise ValueError(f"{dst} contains a forbidden dash character")
        out = ROOT / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        trace[dst] = {k: metrics[k]["display"] for k in sorted(set(used))}
    (AUDIT_PATH.parent / "doc_trace.json").write_text(
        json.dumps(trace, indent=2), encoding="utf-8"
    )
    (ROOT / "data" / "README.md").write_text(data_readme(), encoding="utf-8")
    return trace
