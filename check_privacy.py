#!/usr/bin/env python3
"""Fail when public research assets contain common direct identifiers."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
PUBLIC_PATTERNS = ("*.csv", "*.json", "*.md", "index.html", "figure*.svg")
STUDENT_ID = re.compile(r"(?i)\bU\d{8}\b")
STUDENT_SOURCE = re.compile(
    r"https?://[^\s\"')<]*(?:github\.io|hf\.space|huggingface\.co/spaces|"
    r"gemini\.google\.com|eeclass\.utaipei\.edu\.tw)"
)
FORBIDDEN_COLUMNS = {"學號", "姓名", "來源", "文本預覽", "作品來源_複核"}
FORBIDDEN_JSON_KEYS = {
    "學號",
    "姓名",
    "student_id",
    "studentId",
    "name",
    "source",
    "url",
    "來源",
    "文本預覽",
    "作品來源_複核",
}


def public_files() -> list[Path]:
    result = set()
    for pattern in PUBLIC_PATTERNS:
        result.update(ROOT.glob(pattern))
    return sorted(path for path in result if path.name != "README.md")


def json_keys(value) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for child in value.values():
            found.update(json_keys(child))
        return found
    if isinstance(value, list):
        found = set()
        for child in value:
            found.update(json_keys(child))
        return found
    return set()


def main() -> int:
    failures: list[str] = []
    if (ROOT / "hw_68852-1.zip").exists():
        failures.append("identifiable source archive still exists: hw_68852-1.zip")

    for path in public_files():
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if STUDENT_ID.search(text):
            failures.append(f"{path.name}: student ID pattern")
        if STUDENT_SOURCE.search(text):
            failures.append(f"{path.name}: student-source URL")

        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                header = next(csv.reader(handle), [])
            forbidden = FORBIDDEN_COLUMNS.intersection(header)
            if forbidden:
                failures.append(f"{path.name}: forbidden columns {sorted(forbidden)}")
        elif path.suffix == ".json":
            try:
                keys = json_keys(json.loads(text))
            except json.JSONDecodeError as exc:
                failures.append(f"{path.name}: invalid JSON ({exc})")
                continue
            forbidden = FORBIDDEN_JSON_KEYS.intersection(keys)
            if forbidden:
                failures.append(f"{path.name}: forbidden keys {sorted(forbidden)}")

    if failures:
        print("Privacy check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Privacy check passed for {len(public_files())} public assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
