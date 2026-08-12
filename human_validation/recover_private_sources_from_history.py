#!/usr/bin/env python3
"""Recover artifact source URLs locally from authorized repository history.

This helper is intended for the study owner/research team. It reads three
pre-anonymization CSV snapshots from Git history, validates their row order
against the public anonymized seed using Media/Layout scores, and writes ONLY
source URLs into an ignored private CSV. Student names/IDs from historical
files are never written to the output.

Run from the repository root on the human-validation branch.
"""

from __future__ import annotations

import argparse
import io
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "human_validation" / "artifact_sources_seed.csv"
DEFAULT_OUTPUT = ROOT / "human_validation" / "private_artifact_sources.csv"

HISTORICAL = {
    "Geophysics_final": {
        "commit": "7414188681f00616f83635c4654c6f4ff2349df8",
        "path": "results_geophysics_2025_final_primary.csv",
    },
    "Seismology_first": {
        "commit": "6f41080be67fb35a52a55c643c00c4bc8ac68ddb",
        "path": "seismology_2026_hw2_results.csv",
    },
    "Seismology_final": {
        "commit": "7690221f6e77f98e0901c1104dde32dba5e19428",
        "path": "results_seismology_2026_final_primary.csv",
    },
}

MEDIA_COL = "媒體豐富度(1-4)"
LAYOUT_COL = "排版架構(1-4)"
SOURCE_COL = "來源"


def git_show_csv(commit: str, path: str) -> pd.DataFrame:
    spec = f"{commit}:{path}"
    try:
        raw = subprocess.check_output(
            ["git", "show", spec],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        msg = exc.output.decode("utf-8", errors="replace")
        raise SystemExit(
            f"Cannot read {spec}. Ensure the repository has full history.\n{msg}"
        ) from exc

    text = raw.decode("utf-8-sig")
    frame = pd.read_csv(io.StringIO(text))
    missing = {MEDIA_COL, LAYOUT_COL, SOURCE_COL} - set(frame.columns)
    if missing:
        raise SystemExit(f"Historical file {spec} missing columns: {sorted(missing)}")
    return frame


def as_int(value, label: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"Invalid {label}: {value!r}") from exc


def validate_stage(seed_stage: pd.DataFrame, old: pd.DataFrame, stage: str) -> None:
    if len(seed_stage) != len(old):
        raise SystemExit(
            f"{stage}: row-count mismatch: seed={len(seed_stage)}, history={len(old)}"
        )

    errors: list[str] = []
    for pos, ((_, seed_row), (_, old_row)) in enumerate(
        zip(seed_stage.iterrows(), old.iterrows(), strict=True), start=1
    ):
        seed_media = as_int(seed_row["automated_media"], "seed media")
        seed_layout = as_int(seed_row["automated_layout"], "seed layout")
        old_media = as_int(old_row[MEDIA_COL], "historical media")
        old_layout = as_int(old_row[LAYOUT_COL], "historical layout")
        if (seed_media, seed_layout) != (old_media, old_layout):
            errors.append(
                f"row {pos} ({seed_row['private_id']}): "
                f"seed=({seed_media},{seed_layout}) history=({old_media},{old_layout})"
            )

    if errors:
        preview = "\n".join(errors[:10])
        raise SystemExit(
            f"{stage}: order/score validation failed; refusing to recover URLs.\n{preview}"
        )


def recover(seed: pd.DataFrame) -> pd.DataFrame:
    required = {
        "private_id",
        "anonymous_code",
        "stage",
        "group",
        "source",
        "automated_media",
        "automated_layout",
        "auto_status",
        "fetch_limitation",
        "include",
    }
    missing = required - set(seed.columns)
    if missing:
        raise SystemExit(f"Seed missing columns: {sorted(missing)}")

    out = seed.copy()
    out["source"] = ""

    for stage, cfg in HISTORICAL.items():
        idx = out.index[out["stage"].eq(stage)].tolist()
        stage_seed = out.loc[idx].copy()
        old = git_show_csv(cfg["commit"], cfg["path"])
        validate_stage(stage_seed, old, stage)

        sources = old[SOURCE_COL].fillna("").astype(str).tolist()
        if any(not s.strip() for s in sources):
            raise SystemExit(f"{stage}: historical file contains blank source URL(s)")
        out.loc[idx, "source"] = sources
        print(f"[ok] {stage}: recovered {len(sources)} source URLs")

    if (out["source"].astype(str).str.strip() == "").any():
        missing_rows = out.loc[
            out["source"].astype(str).str.strip().eq(""), "private_id"
        ].tolist()
        raise SystemExit(f"Unfilled source rows remain: {missing_rows[:10]}")

    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recover authorized artifact source URLs from local Git history."
    )
    parser.add_argument("--seed", default=str(DEFAULT_SEED))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing private output file.",
    )
    args = parser.parse_args()

    seed_path = Path(args.seed)
    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        raise SystemExit(
            f"Refusing to overwrite existing {output_path}. Use --force if intended."
        )

    seed = pd.read_csv(seed_path, dtype=str).fillna("")
    recovered = recover(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    recovered.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"[saved-private] {output_path}")
    print(f"[count] {len(recovered)} artifacts")
    print("Do NOT git add/commit this output. It is ignored by human_validation/.gitignore.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
