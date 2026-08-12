#!/usr/bin/env python3
"""Create a blinded, stratified sentence sample for reflection coding."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analyze_web import (  # noqa: E402
    DESCRIBE_MARKERS,
    REFLECTION_MARKERS,
    analyze_text_density,
    load_html,
)

REQUIRED = {"private_id", "stage", "source"}


def truthy(value) -> bool:
    if pd.isna(value):
        return True
    return str(value).strip().lower() not in {"0", "false", "no", "n", "exclude"}


def resolve_source(source: str, input_csv: Path) -> str:
    """Resolve local relative sources against the private CSV directory."""
    source = source.strip()
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        return source
    path = Path(source).expanduser()
    if path.is_absolute():
        return str(path)
    return str((input_csv.parent / path).resolve())


def split_sentences(text: str, min_chars: int = 12) -> list[str]:
    raw = re.split(r"(?<=[。！？!?])\s*|\n+", text)
    cleaned: list[str] = []
    for sentence in raw:
        sentence = re.sub(r"\s+", " ", sentence).strip()
        if len(sentence) < min_chars:
            continue
        if len(sentence) > 600:
            continue
        cleaned.append(sentence)
    return cleaned


def automated_binary(sentence: str) -> str:
    low = sentence.lower()
    c_hits = sum(1 for marker in REFLECTION_MARKERS if marker.lower() in low)
    d_hits = sum(1 for marker in DESCRIBE_MARKERS if marker.lower() in low)
    return "CR" if c_hits > d_hits and c_hits > 0 else "NON_CR"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sample sentences across stages for blinded human coding."
    )
    parser.add_argument("--input", required=True, help="Private source CSV")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sample-size", type=int, default=300)
    parser.add_argument("--max-per-artifact", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260810)
    args = parser.parse_args()

    input_csv = Path(args.input).expanduser().resolve()
    src = pd.read_csv(input_csv, dtype=str)
    missing = REQUIRED - set(src.columns)
    if missing:
        raise SystemExit(f"Missing columns: {sorted(missing)}")
    if "include" in src.columns:
        src = src[src["include"].map(truthy)].copy()

    rows: list[dict] = []
    for _, item in src.iterrows():
        private_id = str(item["private_id"])
        stage = str(item["stage"])
        source = resolve_source(str(item["source"]), input_csv)
        try:
            html = load_html(source)
            _, _, _, text, _ = analyze_text_density(html)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] {private_id}: {exc}", file=sys.stderr)
            continue

        sentences = split_sentences(text)
        if len(sentences) > args.max_per_artifact:
            frame = pd.Series(sentences)
            sentences = frame.sample(
                n=args.max_per_artifact,
                random_state=args.seed + len(rows),
            ).tolist()
        for sentence in sentences:
            rows.append(
                {
                    "private_id": private_id,
                    "stage": stage,
                    "sentence": sentence,
                    "automated_binary": automated_binary(sentence),
                }
            )

    pool = pd.DataFrame(rows)
    if pool.empty:
        raise SystemExit("No usable sentences were extracted.")

    stages = sorted(pool["stage"].dropna().unique().tolist())
    if not stages:
        raise SystemExit("No stage labels found.")

    target = min(args.sample_size, len(pool))
    base = target // len(stages)
    remainder = target % len(stages)
    selected_parts = []
    selected_indices: set[int] = set()

    for i, stage in enumerate(stages):
        stage_pool = pool[pool["stage"].eq(stage)]
        quota = base + (1 if i < remainder else 0)
        n = min(quota, len(stage_pool))
        chosen = stage_pool.sample(n=n, random_state=args.seed + i)
        selected_parts.append(chosen)
        selected_indices.update(chosen.index.tolist())

    selected = pd.concat(selected_parts, ignore_index=False) if selected_parts else pool.iloc[0:0]

    shortage = target - len(selected)
    if shortage > 0:
        remaining = pool.loc[~pool.index.isin(selected_indices)]
        fill = remaining.sample(
            n=min(shortage, len(remaining)),
            random_state=args.seed + 999,
        )
        selected = pd.concat([selected, fill], ignore_index=False)

    selected = selected.sample(frac=1, random_state=args.seed + 5000).reset_index(drop=True)
    selected.insert(0, "sentence_id", [f"T{i:04d}" for i in range(1, len(selected) + 1)])

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    key = selected[[
        "sentence_id",
        "private_id",
        "stage",
        "sentence",
        "automated_binary",
    ]].copy()
    key.to_csv(out / "sentence_key.csv", index=False, encoding="utf-8-sig")

    rating = selected[["sentence_id", "sentence"]].copy()
    rating["human_code"] = ""
    rating["note"] = ""
    rating.to_csv(out / "rater_A_sentences.csv", index=False, encoding="utf-8-sig")
    rating.to_csv(out / "rater_B_sentences.csv", index=False, encoding="utf-8-sig")

    print(f"Sentence pool: {len(pool)}")
    print(f"Selected: {len(selected)}")
    print("By stage:")
    print(selected["stage"].value_counts().sort_index().to_string())
    print(f"Private key: {out / 'sentence_key.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
