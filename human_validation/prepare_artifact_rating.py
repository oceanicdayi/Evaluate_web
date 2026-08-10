#!/usr/bin/env python3
"""Prepare blinded artifact-rating sheets for two human raters."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED = {
    "private_id",
    "stage",
    "group",
    "source",
    "automated_media",
    "automated_layout",
}


def truthy(value) -> bool:
    if pd.isna(value):
        return True
    return str(value).strip().lower() not in {"0", "false", "no", "n", "exclude"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create randomized, blinded Media/Layout rating sheets."
    )
    parser.add_argument("--input", required=True, help="Private source CSV")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument(
        "--omit-source",
        action="store_true",
        help="Do not place source URL/path in rater sheets; use a separate private packet.",
    )
    args = parser.parse_args()

    src = pd.read_csv(args.input, dtype=str)
    missing = REQUIRED - set(src.columns)
    if missing:
        raise SystemExit(f"Missing columns: {sorted(missing)}")

    if "include" in src.columns:
        src = src[src["include"].map(truthy)].copy()

    if src["private_id"].duplicated().any():
        dup = src.loc[src["private_id"].duplicated(), "private_id"].tolist()
        raise SystemExit(f"Duplicate private_id values: {dup[:5]}")

    src = src.sample(frac=1, random_state=args.seed).reset_index(drop=True)
    src.insert(0, "artifact_id", [f"A{i:03d}" for i in range(1, len(src) + 1)])

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    key_cols = [
        "artifact_id",
        "private_id",
        "stage",
        "group",
        "source",
        "automated_media",
        "automated_layout",
    ]
    key = src[key_cols].copy()
    key.to_csv(out / "artifact_key.csv", index=False, encoding="utf-8-sig")

    rating = pd.DataFrame({
        "artifact_id": src["artifact_id"],
        "media_score": "",
        "layout_score": "",
        "media_note": "",
        "layout_note": "",
    })
    if not args.omit_source:
        rating.insert(1, "review_source", src["source"].values)

    rating.to_csv(out / "rater_A_artifacts.csv", index=False, encoding="utf-8-sig")
    rating.to_csv(out / "rater_B_artifacts.csv", index=False, encoding="utf-8-sig")

    print(f"Prepared {len(src)} artifacts")
    print(f"Private key: {out / 'artifact_key.csv'}")
    print(f"Rater A: {out / 'rater_A_artifacts.csv'}")
    print(f"Rater B: {out / 'rater_B_artifacts.csv'}")
    if not args.omit_source:
        print("Note: source is visible to raters, but stage/group/automated scores are hidden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
