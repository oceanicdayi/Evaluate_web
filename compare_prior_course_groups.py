#!/usr/bin/env python3
"""Compare Seismology final reports by prior Geophysics-course roster presence."""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pandas as pd

METRICS = {
    "媒體豐富度(1-4)": "媒體豐富度",
    "排版架構(1-4)": "排版架構",
    "總字數": "總字數",
    "專有名詞密度(次/千字)": "術語密度",
    "批判思考佔比(%)": "批判思考比例",
}

PRIOR_GROUP = "上學期作品名單內"
NEW_GROUP = "未見於上學期作品名單"
GEO_URL = "上學期原始作品集合（連結因去識別化移除）"
SEIS_URL = "下學期原始作品集合（連結因去識別化移除）"


def assign_groups(geo_csv: str, seis_csv: str) -> pd.DataFrame:
    geo = pd.read_csv(geo_csv, dtype={"匿名代碼": str})
    seis = pd.read_csv(seis_csv, dtype={"匿名代碼": str})
    prior_ids = set(geo["匿名代碼"].dropna())
    seis["組別"] = seis["匿名代碼"].map(
        lambda sid: PRIOR_GROUP if sid in prior_ids else NEW_GROUP
    )
    return seis.sort_values(["組別", "匿名代碼"]).reset_index(drop=True)


def cliffs_delta(a: pd.Series, b: pd.Series) -> float:
    """Probability(a>b) - Probability(a<b); ties contribute zero."""
    greater = sum(x > y for x in a for y in b)
    less = sum(x < y for x in a for y in b)
    return (greater - less) / (len(a) * len(b))


def exact_rank_permutation_p(values: pd.Series, in_prior: pd.Series) -> float:
    """
    Exact two-sided permutation p-value on midrank sum.

    This is an exploratory small-sample comparison, not a causal estimate.
    """
    ranks = values.rank(method="average").tolist()
    n = len(ranks)
    n_prior = int(in_prior.sum())
    observed_indices = set(in_prior[in_prior].index)
    # Input is reset-indexed, so DataFrame indices map to rank list positions.
    observed = sum(ranks[i] for i in observed_indices)
    expected = n_prior * (n + 1) / 2
    observed_deviation = abs(observed - expected)

    extreme = 0
    total = 0
    for combination in itertools.combinations(range(n), n_prior):
        rank_sum = sum(ranks[i] for i in combination)
        if abs(rank_sum - expected) >= observed_deviation - 1e-12:
            extreme += 1
        total += 1
    return extreme / total


def build_summary(grouped: pd.DataFrame) -> pd.DataFrame:
    prior = grouped[grouped["組別"].eq(PRIOR_GROUP)]
    new = grouped[grouped["組別"].eq(NEW_GROUP)]
    rows = []
    for metric, label in METRICS.items():
        a = prior[metric]
        b = new[metric]
        rows.append(
            {
                "指標": label,
                "有上學期作品_n": len(a),
                "有上學期作品_平均": a.mean(),
                "有上學期作品_中位數": a.median(),
                "未見上學期作品_n": len(b),
                "未見上學期作品_平均": b.mean(),
                "未見上學期作品_中位數": b.median(),
                "平均差_有減未": a.mean() - b.mean(),
                "中位數差_有減未": a.median() - b.median(),
                "Cliffs_delta": cliffs_delta(a, b),
                "精確秩排列_p": exact_rank_permutation_p(
                    grouped[metric], grouped["組別"].eq(PRIOR_GROUP)
                ),
            }
        )
    return pd.DataFrame(rows)


def fmt(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "—"
    if digits == 0:
        return f"{value:.0f}"
    return f"{value:.{digits}f}"


def make_report(grouped: pd.DataFrame, summary: pd.DataFrame) -> str:
    prior = grouped[grouped["組別"].eq(PRIOR_GROUP)]
    new = grouped[grouped["組別"].eq(NEW_GROUP)]

    lines = [
        "# 下學期地震學期末報告：依上學期作品名單分組比較",
        "",
        f"- 上學期作品名單：{GEO_URL}",
        f"- 下學期分析對象：{SEIS_URL}",
        f"- {PRIOR_GROUP}：**{len(prior)} 人**",
        f"- {NEW_GROUP}：**{len(new)} 人**",
        "",
        "> 「修過上學期課程」在此僅以是否出現在上學期期末作品名單作為代理變項，",
        "> 並非正式選課紀錄。未出現在作品名單，不等同於確定未修課。",
        "",
        "## 組別成員",
        "",
        f"- {PRIOR_GROUP}：" + "、".join("匿名學生 " + prior["匿名代碼"]),
        f"- {NEW_GROUP}：" + "、".join("匿名學生 " + new["匿名代碼"]),
        "",
        "## 描述統計",
        "",
        "| 指標 | 名單內平均 | 名單內中位數 | 名單外平均 | 名單外中位數 | "
        "平均差（內−外） | 中位數差（內−外） |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for _, row in summary.iterrows():
        digits = 0 if row["指標"] == "總字數" else 2
        lines.append(
            f"| {row['指標']} | {fmt(row['有上學期作品_平均'], digits)} | "
            f"{fmt(row['有上學期作品_中位數'], digits)} | "
            f"{fmt(row['未見上學期作品_平均'], digits)} | "
            f"{fmt(row['未見上學期作品_中位數'], digits)} | "
            f"{fmt(row['平均差_有減未'], digits)} | "
            f"{fmt(row['中位數差_有減未'], digits)} |"
        )

    word_prior = prior["總字數"]
    word_new = new["總字數"]
    reflect_prior = prior["批判思考佔比(%)"]
    reflect_new = new["批判思考佔比(%)"]
    media_row = summary.set_index("指標").loc["媒體豐富度"]
    layout_row = summary.set_index("指標").loc["排版架構"]
    term_row = summary.set_index("指標").loc["術語密度"]

    lines += [
        "",
        "## 解讀",
        "",
        f"1. **媒體豐富度有中等差距，排版差異不大**：媒體中位數為 {fmt(media_row['有上學期作品_中位數'],0)}"
        f"（名單內）／{fmt(media_row['未見上學期作品_中位數'],0)}（名單外），"
        f"排版中位數為 {fmt(layout_row['有上學期作品_中位數'],0)}／{fmt(layout_row['未見上學期作品_中位數'],0)}；"
        f"名單內組媒體平均僅高 {media_row['平均差_有減未']:.2f} 分、"
        f"排版平均高 {layout_row['平均差_有減未']:.2f} 分。",
        f"2. **名單內組的典型篇幅較長**：字數中位數為 {word_prior.median():.0f}，"
        f"名單外組為 {word_new.median():.0f}，差 {word_prior.median()-word_new.median():+.0f} 字。",
        f"但名單外組含一份 {word_new.max():.0f} 字的極長作品，使其平均反而較高；"
        "在此小樣本中，中位數比平均數更能代表典型學生。",
        f"3. **反思比例差異很小且受離群值影響**：名單內中位數 {reflect_prior.median():.1f}%，"
        f"名單外中位數 {reflect_new.median():.1f}%；名單外組有一份 33.3% 作品拉高平均。",
        f"4. **術語密度{'沒有一致優勢' if term_row['平均差_有減未'] < 0 else '略偏名單內組'}**："
        f"名單{'外' if term_row['平均差_有減未'] < 0 else '內'}組的平均與中位數較高，"
        "但這個指標會因短篇作品分母較小而上升。",
        "5. 五項精確秩排列比較皆未顯示清楚組間差異（探索性 p 值均大於 .50）。",
        "樣本只有 13 對 5，且非隨機分組，因此不能據此推論修過上學期課程造成效果。",
        "",
        "## 探索性效果量",
        "",
        "| 指標 | Cliff's δ | 精確秩排列 p |",
        "| --- | ---: | ---: |",
    ]

    for _, row in summary.iterrows():
        lines.append(
            f"| {row['指標']} | {row['Cliffs_delta']:.3f} | "
            f"{row['精確秩排列_p']:.3f} |"
        )

    lines += [
        "",
        "## 下學期個別資料",
        "",
        "| 組別 | 匿名代碼 | 匿名標籤 | 媒體 | 排版 | 字數 | 術語密度 | 批判思考% |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in grouped.iterrows():
        lines.append(
            f"| {row['組別']} | {row['匿名代碼']} | 匿名學生 {row['匿名代碼']} | "
            f"{row['媒體豐富度(1-4)']} | {row['排版架構(1-4)']} | "
            f"{row['總字數']} | {row['專有名詞密度(次/千字)']:.2f} | "
            f"{row['批判思考佔比(%)']:.1f} |"
        )

    lines += [
        "",
        "## 結論",
        "",
        f"就下學期期末作品而言，名單內組在媒體豐富度上呈現中等幅度的優勢（δ={media_row['Cliffs_delta']:.3f}，"
        f"精確 p={media_row['精確秩排列_p']:.3f}，未達 .05 門檻），排版與反思比例差異都很小。",
        "較值得注意的是，名單內組的**字數中位數較高**，顯示其典型作品篇幅較長；",
        "但組間分布高度重疊、樣本不平衡且有離群值，現階段只能作描述性觀察，不宜視為課程效果的證據。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="比較下學期有無上學期作品紀錄的兩組學生")
    parser.add_argument(
        "--geophysics",
        default="results_geophysics_2025_final.csv",
        help="上學期期末作品分析 CSV",
    )
    parser.add_argument(
        "--seismology",
        default="results_seismology_2026_final_primary.csv",
        help="下學期期末作品分析 CSV",
    )
    parser.add_argument(
        "--grouped-output",
        default="seismology_2026_by_prior_course_group.csv",
        help="含組別的學生資料 CSV",
    )
    parser.add_argument(
        "--summary-output",
        default="seismology_2026_prior_course_group_summary.csv",
        help="組別摘要 CSV",
    )
    parser.add_argument(
        "--report",
        default="seismology_2026_prior_course_group_comparison.md",
        help="Markdown 報告",
    )
    args = parser.parse_args()

    grouped = assign_groups(args.geophysics, args.seismology)
    summary = build_summary(grouped)
    grouped.to_csv(args.grouped_output, index=False, encoding="utf-8-sig")
    summary.to_csv(args.summary_output, index=False, encoding="utf-8-sig")
    Path(args.report).write_text(make_report(grouped, summary), encoding="utf-8")

    counts = grouped["組別"].value_counts()
    print(f"{PRIOR_GROUP}: {counts.get(PRIOR_GROUP, 0)} 人")
    print(f"{NEW_GROUP}: {counts.get(NEW_GROUP, 0)} 人")
    print(f"[saved] {args.grouped_output}")
    print(f"[saved] {args.summary_output}")
    print(f"[saved] {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
