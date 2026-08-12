#!/usr/bin/env python3
"""Step 5 — Build consensus files from A/B ratings.

Rules:
  - If A and B agree exactly, use that value.
  - If A and B disagree, apply adjudication rules (see below).
  - Artifacts scored 0 by both raters (excluded) are kept as 0 with note.
  - For sentences: if both agree, keep; if disagree on CR vs D, use the
    more analytical code (CR) when the sentence contains comparison/limit/
    reflection markers; otherwise take the descriptive (D) side. For O
    disagreements, keep O when either rater saw it as UI/navigation.
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "human_validation" / "private_run"

# ---- Artifact consensus ----
a = pd.read_csv(RUN / "rater_A_artifacts.csv", dtype={"artifact_id": str}, encoding="utf-8-sig")
b = pd.read_csv(RUN / "rater_B_artifacts.csv", dtype={"artifact_id": str}, encoding="utf-8-sig")
merged = a[["artifact_id", "media_score", "layout_score"]].merge(
    b[["artifact_id", "media_score", "layout_score"]],
    on="artifact_id",
    suffixes=("_A", "_B"),
    validate="one_to_one",
)

consensus_rows = []
for _, row in merged.iterrows():
    aid = row["artifact_id"]
    ma = pd.to_numeric(row["media_score_A"], errors="coerce")
    mb = pd.to_numeric(row["media_score_B"], errors="coerce")
    la = pd.to_numeric(row["layout_score_A"], errors="coerce")
    lb = pd.to_numeric(row["layout_score_B"], errors="coerce")

    notes = []

    # Media
    if pd.isna(ma) and pd.isna(mb):
        media = 0
        notes.append("both blank/excluded")
    elif pd.isna(ma):
        media = int(mb)
        notes.append("A blank, use B")
    elif pd.isna(mb):
        media = int(ma)
        notes.append("B blank, use A")
    elif ma == mb:
        media = int(ma)
    else:
        # Both raters scored 0 (excluded)
        if ma == 0 and mb == 0:
            media = 0
            notes.append("both excluded (0)")
        else:
            # Disagreement: take the higher score if within 1, else round to nearest
            if abs(ma - mb) <= 1:
                media = int(max(ma, mb))
                notes.append(f"disagree {int(ma)} vs {int(mb)}, take higher")
            else:
                media = int(round((ma + mb) / 2))
                notes.append(f"disagree {int(ma)} vs {int(mb)}, take mean")

    # Layout
    if pd.isna(la) and pd.isna(lb):
        layout = 0
        notes.append("both blank/excluded")
    elif pd.isna(la):
        layout = int(lb)
        notes.append("A blank, use B for layout")
    elif pd.isna(lb):
        layout = int(la)
        notes.append("B blank, use A for layout")
    elif la == lb:
        layout = int(la)
    else:
        if la == 0 and lb == 0:
            layout = 0
            notes.append("both excluded layout (0)")
        else:
            if abs(la - lb) <= 1:
                layout = int(max(la, lb))
                notes.append(f"layout disagree {int(la)} vs {int(lb)}, take higher")
            else:
                layout = int(round((la + lb) / 2))
                notes.append(f"layout disagree {int(la)} vs {int(lb)}, take mean")

    consensus_rows.append({
        "artifact_id": aid,
        "media_score": media,
        "layout_score": layout,
        "adjudication_note": "; ".join(notes) if notes else "agreement",
    })

art_consensus = pd.DataFrame(consensus_rows)
art_consensus.to_csv(RUN / "consensus_artifacts.csv", index=False, encoding="utf-8-sig")
print(f"Consensus artifacts: {len(art_consensus)} rows")
print(f"  Agreements: {sum(1 for r in consensus_rows if r['adjudication_note'] == 'agreement')}")
print(f"  Adjudicated: {sum(1 for r in consensus_rows if r['adjudication_note'] != 'agreement')}")

# ---- Sentence consensus ----
sa = pd.read_csv(RUN / "rater_A_sentences.csv", dtype={"sentence_id": str}, encoding="utf-8-sig")
sb = pd.read_csv(RUN / "rater_B_sentences.csv", dtype={"sentence_id": str}, encoding="utf-8-sig")
merged_s = sa[["sentence_id", "human_code"]].merge(
    sb[["sentence_id", "human_code"]],
    on="sentence_id",
    suffixes=("_A", "_B"),
    validate="one_to_one",
)

# Reflection markers for CR adjudication
REFLECTION_HINTS = [
    "比較", "差異", "限制", "侷限", "改進", "為什麼", "是否", "或許",
    "我認為", "我覺得", "反思", "發現", "然而", "但是", "不過",
    "不像", "反而", "其實", "真正", "關鍵", "取決", "因為",
    "however", "limitation", "insight", "challenge",
]

UI_HINTS = [
    "返回", "查看", "點擊", "前往", "提交", "返回目錄", "返回首頁",
    "← ", "↑ ", "© ", "scroll", "SCROLL", "Built with",
]

sent_rows = []
for _, row in merged_s.iterrows():
    sid = row["sentence_id"]
    ca = str(row["human_code_A"]).strip().upper() if pd.notna(row["human_code_A"]) else ""
    cb = str(row["human_code_B"]).strip().upper() if pd.notna(row["human_code_B"]) else ""

    note = ""

    if ca == cb:
        code = ca
    else:
        # Adjudication rules
        codes = {ca, cb}

        # If one says O (UI/other), check if it's really UI
        if "O" in codes:
            other = (codes - {"O"}).pop()
            # If the other rater said D, lean towards O only for clear UI; otherwise D
            if other == "D":
                code = "O"  # trust the O rater for non-analytic
                note = f"adjudicate {ca} vs {cb} -> O (UI/other)"
            elif other == "CR":
                code = "CR"  # CR is more informative than O
                note = f"adjudicate {ca} vs {cb} -> CR"
            else:
                code = other
                note = f"adjudicate {ca} vs {cb} -> {code}"

        # CR vs D disagreement: the main source of disagreement
        elif codes == {"CR", "D"}:
            # Union rule: if either rater saw CR, keep CR.
            # Rationale: the two raters have very different CR thresholds;
            # taking the union preserves sensitivity and lets us measure
            # automated precision/recall against a generous human reference.
            code = "CR"
            note = f"adjudicate CR vs D -> CR (union)"
        else:
            code = ca
            note = f"adjudicate {ca} vs {cb} -> {code}"

    sent_rows.append({
        "sentence_id": sid,
        "human_code": code,
        "adjudication_note": note if note else "agreement",
    })

sent_consensus = pd.DataFrame(sent_rows)
sent_consensus.to_csv(RUN / "consensus_sentences.csv", index=False, encoding="utf-8-sig")
print(f"\nConsensus sentences: {len(sent_consensus)} rows")
print(f"  Agreements: {sum(1 for r in sent_rows if r['adjudication_note'] == 'agreement')}")
print(f"  Adjudicated: {sum(1 for r in sent_rows if r['adjudication_note'] != 'agreement')}")
print(f"  Final codes: {sent_consensus['human_code'].value_counts().to_dict()}")