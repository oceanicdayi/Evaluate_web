#!/usr/bin/env python3
"""Compute inter-rater reliability and optional human-vs-automated validation."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd

ORDINAL_CATS = [1, 2, 3, 4]
SENTENCE_CODES = {"D", "CR", "O"}


def weighted_kappa(a: pd.Series, b: pd.Series, categories, kind: str = "quadratic") -> float:
    """Cohen's weighted kappa using disagreement weights."""
    a = pd.Series(a).reset_index(drop=True)
    b = pd.Series(b).reset_index(drop=True)
    if len(a) != len(b) or len(a) == 0:
        return float("nan")
    cats = list(categories)
    index = {cat: i for i, cat in enumerate(cats)}
    k = len(cats)
    obs = pd.DataFrame(0.0, index=cats, columns=cats)
    for x, y in zip(a, b):
        if x not in index or y not in index:
            continue
        obs.loc[x, y] += 1
    n = obs.values.sum()
    if n == 0:
        return float("nan")
    obs /= n
    pa = obs.sum(axis=1).values
    pb = obs.sum(axis=0).values

    observed_disagreement = 0.0
    expected_disagreement = 0.0
    denom = max(k - 1, 1)
    for i in range(k):
        for j in range(k):
            if kind == "linear":
                d = abs(i - j) / denom
            elif kind == "quadratic":
                d = ((i - j) / denom) ** 2
            elif kind == "unweighted":
                d = 0.0 if i == j else 1.0
            else:
                raise ValueError(f"Unknown weight kind: {kind}")
            observed_disagreement += d * obs.iloc[i, j]
            expected_disagreement += d * pa[i] * pb[j]
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else float("nan")
    return 1.0 - observed_disagreement / expected_disagreement


def fmt(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NA"
    return f"{value:.3f}"


def ordinal_pair(a_path: str, b_path: str, metric: str) -> tuple[dict, pd.DataFrame]:
    a = pd.read_csv(a_path, dtype={"artifact_id": str})
    b = pd.read_csv(b_path, dtype={"artifact_id": str})
    merged = a[["artifact_id", metric]].merge(
        b[["artifact_id", metric]], on="artifact_id", suffixes=("_A", "_B"), validate="one_to_one"
    )
    ca, cb = f"{metric}_A", f"{metric}_B"
    merged[ca] = pd.to_numeric(merged[ca], errors="coerce")
    merged[cb] = pd.to_numeric(merged[cb], errors="coerce")
    valid = merged.dropna(subset=[ca, cb]).copy()
    if not valid.empty:
        valid[ca] = valid[ca].astype(int)
        valid[cb] = valid[cb].astype(int)
    valid = valid[valid[ca].isin(ORDINAL_CATS) & valid[cb].isin(ORDINAL_CATS)]
    exact = float((valid[ca] == valid[cb]).mean()) if len(valid) else float("nan")
    within_one = float((valid[ca].sub(valid[cb]).abs() <= 1).mean()) if len(valid) else float("nan")
    stats = {
        "n": len(valid),
        "exact": exact,
        "within_one": within_one,
        "linear_kappa": weighted_kappa(valid[ca], valid[cb], ORDINAL_CATS, "linear"),
        "quadratic_kappa": weighted_kappa(valid[ca], valid[cb], ORDINAL_CATS, "quadratic"),
    }
    disagree = valid[valid[ca] != valid[cb]].copy()
    return stats, disagree


def normalize_sentence_code(value) -> str | None:
    if pd.isna(value):
        return None
    code = str(value).strip().upper().replace(" ", "_")
    aliases = {
        "DESCRIPTIVE": "D",
        "CRITICAL": "CR",
        "REFLECTIVE": "CR",
        "CRITICAL_REFLECTIVE": "CR",
        "OTHER": "O",
    }
    code = aliases.get(code, code)
    return code if code in SENTENCE_CODES else None


def human_binary(code: str | None) -> str | None:
    if code is None:
        return None
    return "CR" if code == "CR" else "NON_CR"


def sentence_pair(a_path: str, b_path: str) -> tuple[dict, pd.DataFrame]:
    a = pd.read_csv(a_path, dtype={"sentence_id": str})
    b = pd.read_csv(b_path, dtype={"sentence_id": str})
    merged = a[["sentence_id", "human_code"]].merge(
        b[["sentence_id", "human_code"]], on="sentence_id", suffixes=("_A", "_B"), validate="one_to_one"
    )
    merged["code_A"] = merged["human_code_A"].map(normalize_sentence_code)
    merged["code_B"] = merged["human_code_B"].map(normalize_sentence_code)
    valid = merged.dropna(subset=["code_A", "code_B"]).copy()
    valid["binary_A"] = valid["code_A"].map(human_binary)
    valid["binary_B"] = valid["code_B"].map(human_binary)

    exact_three = float((valid["code_A"] == valid["code_B"]).mean()) if len(valid) else float("nan")
    exact_binary = float((valid["binary_A"] == valid["binary_B"]).mean()) if len(valid) else float("nan")
    stats = {
        "n": len(valid),
        "exact_3class": exact_three,
        "kappa_3class": weighted_kappa(valid["code_A"], valid["code_B"], ["D", "CR", "O"], "unweighted"),
        "exact_binary": exact_binary,
        "kappa_binary": weighted_kappa(valid["binary_A"], valid["binary_B"], ["CR", "NON_CR"], "unweighted"),
    }
    disagree = valid[valid["code_A"] != valid["code_B"]].copy()
    return stats, disagree


def auto_artifact_validation(consensus_path: str, key_path: str) -> list[str]:
    consensus = pd.read_csv(consensus_path, dtype={"artifact_id": str})
    key = pd.read_csv(key_path, dtype={"artifact_id": str})
    merged = consensus.merge(
        key[["artifact_id", "automated_media", "automated_layout"]],
        on="artifact_id",
        validate="one_to_one",
    )
    lines = ["## Human consensus vs automated artifact scores", ""]
    for human_col, auto_col, label in (
        ("media_score", "automated_media", "Media"),
        ("layout_score", "automated_layout", "Layout"),
    ):
        h = pd.to_numeric(merged[human_col], errors="coerce")
        a = pd.to_numeric(merged[auto_col], errors="coerce")
        valid = pd.DataFrame({"human": h, "auto": a}).dropna()
        valid = valid[valid["human"].isin(ORDINAL_CATS) & valid["auto"].isin(ORDINAL_CATS)]
        exact = (valid["human"] == valid["auto"]).mean() if len(valid) else float("nan")
        qk = weighted_kappa(valid["human"].astype(int), valid["auto"].astype(int), ORDINAL_CATS, "quadratic")
        lk = weighted_kappa(valid["human"].astype(int), valid["auto"].astype(int), ORDINAL_CATS, "linear")
        lines.append(
            f"- {label}: n={len(valid)}, exact={fmt(exact)}, linear weighted κ={fmt(lk)}, quadratic weighted κ={fmt(qk)}"
        )
    lines.append("")
    return lines


def auto_sentence_validation(consensus_path: str, key_path: str) -> list[str]:
    consensus = pd.read_csv(consensus_path, dtype={"sentence_id": str})
    key = pd.read_csv(key_path, dtype={"sentence_id": str})
    merged = consensus.merge(
        key[["sentence_id", "automated_binary"]], on="sentence_id", validate="one_to_one"
    )
    merged["human_code_norm"] = merged["human_code"].map(normalize_sentence_code)
    merged["human_binary"] = merged["human_code_norm"].map(human_binary)
    valid = merged.dropna(subset=["human_binary", "automated_binary"]).copy()
    valid = valid[valid["automated_binary"].isin(["CR", "NON_CR"])]

    tp = int(((valid["human_binary"] == "CR") & (valid["automated_binary"] == "CR")).sum())
    fp = int(((valid["human_binary"] == "NON_CR") & (valid["automated_binary"] == "CR")).sum())
    fn = int(((valid["human_binary"] == "CR") & (valid["automated_binary"] == "NON_CR")).sum())
    tn = int(((valid["human_binary"] == "NON_CR") & (valid["automated_binary"] == "NON_CR")).sum())
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else float("nan")
    accuracy = (tp + tn) / len(valid) if len(valid) else float("nan")
    kappa = weighted_kappa(valid["human_binary"], valid["automated_binary"], ["CR", "NON_CR"], "unweighted")

    return [
        "## Human consensus vs automated reflection heuristic",
        "",
        f"- n={len(valid)}; TP={tp}, FP={fp}, FN={fn}, TN={tn}",
        f"- accuracy={fmt(accuracy)}, precision={fmt(precision)}, recall={fmt(recall)}, F1={fmt(f1)}, Cohen's κ={fmt(kappa)}",
        "",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute human-rating reliability.")
    parser.add_argument("--artifact-a", required=True)
    parser.add_argument("--artifact-b", required=True)
    parser.add_argument("--sentence-a", required=True)
    parser.add_argument("--sentence-b", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--artifact-key")
    parser.add_argument("--sentence-key")
    parser.add_argument("--artifact-consensus")
    parser.add_argument("--sentence-consensus")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    media, media_dis = ordinal_pair(args.artifact_a, args.artifact_b, "media_score")
    layout, layout_dis = ordinal_pair(args.artifact_a, args.artifact_b, "layout_score")
    sentence, sentence_dis = sentence_pair(args.sentence_a, args.sentence_b)

    # One artifact disagreement file containing both scores and optional notes.
    a_art = pd.read_csv(args.artifact_a, dtype={"artifact_id": str})
    b_art = pd.read_csv(args.artifact_b, dtype={"artifact_id": str})
    art_all = a_art.merge(b_art, on="artifact_id", suffixes=("_A", "_B"), validate="one_to_one")
    ma = pd.to_numeric(art_all["media_score_A"], errors="coerce")
    mb = pd.to_numeric(art_all["media_score_B"], errors="coerce")
    la = pd.to_numeric(art_all["layout_score_A"], errors="coerce")
    lb = pd.to_numeric(art_all["layout_score_B"], errors="coerce")
    art_dis = art_all[(ma != mb) | (la != lb)].copy()
    art_dis.to_csv(out / "artifact_disagreements.csv", index=False, encoding="utf-8-sig")

    # Add sentence text back when available from either rating sheet.
    a_sent = pd.read_csv(args.sentence_a, dtype={"sentence_id": str})
    sentence_dis = sentence_dis.merge(
        a_sent[[c for c in ["sentence_id", "sentence"] if c in a_sent.columns]],
        on="sentence_id",
        how="left",
    )
    sentence_dis.to_csv(out / "sentence_disagreements.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Human validation reliability results",
        "",
        "## Inter-rater reliability: artifact rubrics",
        "",
        f"- Media: n={media['n']}, exact={fmt(media['exact'])}, within-one={fmt(media['within_one'])}, linear weighted κ={fmt(media['linear_kappa'])}, quadratic weighted κ={fmt(media['quadratic_kappa'])}",
        f"- Layout: n={layout['n']}, exact={fmt(layout['exact'])}, within-one={fmt(layout['within_one'])}, linear weighted κ={fmt(layout['linear_kappa'])}, quadratic weighted κ={fmt(layout['quadratic_kappa'])}",
        "",
        "## Inter-rater reliability: sentence coding",
        "",
        f"- Three-class D/CR/O: n={sentence['n']}, exact={fmt(sentence['exact_3class'])}, Cohen's κ={fmt(sentence['kappa_3class'])}",
        f"- CR vs non-CR: n={sentence['n']}, exact={fmt(sentence['exact_binary'])}, Cohen's κ={fmt(sentence['kappa_binary'])}",
        "",
        "> Reliability is computed before adjudication. Keep the original A/B files unchanged.",
        "",
    ]

    if args.artifact_consensus and args.artifact_key:
        lines.extend(auto_artifact_validation(args.artifact_consensus, args.artifact_key))
    if args.sentence_consensus and args.sentence_key:
        lines.extend(auto_sentence_validation(args.sentence_consensus, args.sentence_key))

    report = "\n".join(lines)
    (out / "validation_results.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"[saved] {out / 'validation_results.md'}")
    print(f"[saved] {out / 'artifact_disagreements.csv'}")
    print(f"[saved] {out / 'sentence_disagreements.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
