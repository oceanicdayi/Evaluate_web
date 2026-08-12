#!/usr/bin/env python3
"""Create calibration sheets for Step 0 — 5 diverse artifacts for rater practice."""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "human_validation" / "private_artifact_sources.csv", dtype=str, encoding="utf-8-sig")

cal_ids = ["GEO_S019", "GEO_S025", "HW2_S003", "HW2_S010", "FINAL_S012"]
cal = df[df["private_id"].isin(cal_ids)].copy()

# Shuffle so raters cannot infer stage order
cal = cal.sample(frac=1, random_state=20260812).reset_index(drop=True)
cal.insert(0, "artifact_id", [f"C{i:02d}" for i in range(1, len(cal) + 1)])

out = ROOT / "human_validation" / "private_run"
out.mkdir(parents=True, exist_ok=True)

# Private key (researcher only)
key = cal[["artifact_id", "private_id", "stage", "group", "source", "automated_media", "automated_layout"]].copy()
key.to_csv(out / "calibration_key.csv", index=False, encoding="utf-8-sig")

# Rater sheets
rater = cal[["artifact_id", "source"]].copy()
rater.rename(columns={"source": "review_source"}, inplace=True)
rater["media_score"] = ""
rater["layout_score"] = ""
rater["media_note"] = ""
rater["layout_note"] = ""
rater.to_csv(out / "calibration_rater_A.csv", index=False, encoding="utf-8-sig")
rater.to_csv(out / "calibration_rater_B.csv", index=False, encoding="utf-8-sig")

print("Calibration artifacts:")
for _, r in cal.iterrows():
    print(f"  {r['artifact_id']} -> {r['private_id']:15s} stage={r['stage']:20s} media={r['automated_media']} layout={r['automated_layout']}")
print()
print(f"Key:     {out / 'calibration_key.csv'}")
print(f"Rater A: {out / 'calibration_rater_A.csv'}")
print(f"Rater B: {out / 'calibration_rater_B.csv'}")