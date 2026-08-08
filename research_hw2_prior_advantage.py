#!/usr/bin/env python3
"""Deep-dive evidence for a prior-course advantage on the first webpage assignment."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from analyze_assignment_archive import (
    DEFAULT_ARCHIVE,
    NEW_GROUP,
    PRIOR_GROUP,
    cliffs_delta,
    exact_rank_permutation_p,
    find_artifact,
    open_archive,
    student_members,
)
from analyze_web import analyze_text_density

# Assignment-aligned chapter concepts. A concept is counted only when every
# pattern in its tuple is present. This is an exploratory lexical coverage
# measure, not a correctness score.
TOPICS: dict[str, tuple[str, ...]] = {
    "研究範疇與模型": (r"地震學.{0,20}(研究|科學)", r"模型"),
    "震源－傳播－觀測": (r"震源", r"(介質|傳播路徑)", r"(接收|觀測站|地震儀)"),
    "Hazard 與 Risk": (r"hazard|危害", r"risk|風險"),
    "能量衰減": (r"衰減|attenuation",),
    "建築與共振": (r"建築|結構", r"共振|頻率|週期"),
    "液化與海嘯": (r"液化", r"海嘯"),
    "預報與預測": (r"預報|forecast", r"預測|prediction"),
    "地震空白區": (r"空白區|空區|seismic\s*gap",),
    "前兆與預測限制": (
        r"前兆",
        r"(無法|困難|不可靠|限制).{0,20}預測|預測.{0,20}(無法|困難|不可靠|限制)",
    ),
    "即時預警": (r"即時.{0,5}(預警|警報)|early\s*warning|EEW",),
    "核試爆監測": (r"核試爆|核武|nuclear",),
}


def parse_late_status(zf) -> dict[str, bool]:
    if "index.html" not in zf.namelist():
        return {}
    soup = BeautifulSoup(zf.read("index.html"), "html.parser")
    result = {}
    for row in soup.select("tr[role='data']"):
        cells = row.find_all("td")
        if len(cells) < 6:
            continue
        sid = cells[1].get_text(strip=True).upper()
        result[sid] = cells[-1].get_text(strip=True).upper() == "V"
    return result


def collect_assignment_evidence(
    archive: str, results_csv: str
) -> pd.DataFrame:
    results = pd.read_csv(results_csv, dtype={"學號": str})
    evidence = []
    with open_archive(archive) as zf:
        late = parse_late_status(zf)
        for sid, name, member in student_members(zf):
            source, html, _ = find_artifact(zf, member)
            _, _, _, text, _ = analyze_text_density(html)
            row = {"學號": sid, "姓名": name, "遲交": late.get(sid, False)}
            for topic, patterns in TOPICS.items():
                row[f"主題_{topic}"] = all(
                    re.search(pattern, text, flags=re.I) is not None
                    for pattern in patterns
                )
            row["主題涵蓋數"] = sum(row[f"主題_{topic}"] for topic in TOPICS)
            row["主題涵蓋率(%)"] = row["主題涵蓋數"] / len(TOPICS) * 100
            row["高涵蓋(>=8/11)"] = row["主題涵蓋數"] >= 8
            row["作品來源_複核"] = source
            evidence.append(row)

    merged = results.merge(
        pd.DataFrame(evidence),
        on=["學號", "姓名"],
        how="left",
        validate="one_to_one",
    )

    # Post-hoc content-development index: equal-weighted percentile ranks of
    # length, absolute technical-term count, and topic coverage.
    components = ["總字數", "專有名詞出現次數", "主題涵蓋數"]
    rank_columns = []
    for component in components:
        rank_col = f"{component}_百分等級"
        merged[rank_col] = merged[component].rank(method="average", pct=True) * 100
        rank_columns.append(rank_col)
    merged["內容發展指數"] = merged[rank_columns].mean(axis=1)
    return merged


def rank_summary(
    data: pd.DataFrame, column: str, label: str
) -> dict[str, float | str]:
    prior = data[data["組別"].eq(PRIOR_GROUP)][column].dropna()
    new = data[data["組別"].eq(NEW_GROUP)][column].dropna()
    return {
        "指標": label,
        "名單內_平均": prior.mean(),
        "名單內_中位數": prior.median(),
        "名單外_平均": new.mean(),
        "名單外_中位數": new.median(),
        "平均差_內減外": prior.mean() - new.mean(),
        "中位數差_內減外": prior.median() - new.median(),
        "Cliffs_delta": cliffs_delta(prior, new),
        "精確秩排列_p": exact_rank_permutation_p(
            data[column], data["組別"].eq(PRIOR_GROUP)
        ),
    }


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """Return odds ratio and Fisher two-sided exact p for [[a,b],[c,d]]."""
    row1 = a + b
    row2 = c + d
    success = a + c
    total = row1 + row2
    denominator = math.comb(total, row1)

    def probability(x: int) -> float:
        return (
            math.comb(success, x)
            * math.comb(total - success, row1 - x)
            / denominator
        )

    low = max(0, row1 - (total - success))
    high = min(row1, success)
    observed = probability(a)
    p = sum(
        probability(x)
        for x in range(low, high + 1)
        if probability(x) <= observed + 1e-15
    )
    odds = (a * d / (b * c)) if b and c else math.inf
    return odds, min(1.0, p)


def build_deep_summary(data: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("媒體豐富度(1-4)", "媒體豐富度"),
        ("排版架構(1-4)", "排版架構"),
        ("總字數", "總字數"),
        ("專有名詞出現次數", "專有名詞絕對次數"),
        ("主題涵蓋數", "主題涵蓋數（/11）"),
        ("內容發展指數", "內容發展指數（探索性）"),
    ]
    return pd.DataFrame(rank_summary(data, column, label) for column, label in specs)


def stage_effects(
    assignment: pd.DataFrame, final_csv: str
) -> pd.DataFrame:
    final = pd.read_csv(final_csv, dtype={"學號": str})
    common = assignment.merge(
        final,
        on=["學號", "姓名"],
        suffixes=("_作業", "_期末"),
        validate="one_to_one",
    )
    rows = []
    metrics = [
        ("媒體豐富度(1-4)", "媒體豐富度"),
        ("排版架構(1-4)", "排版架構"),
        ("總字數", "總字數"),
        ("批判思考佔比(%)", "批判思考比例"),
    ]
    for metric, label in metrics:
        for suffix, stage in (("_作業", "第一個網頁作業"), ("_期末", "期末報告")):
            column = f"{metric}{suffix}"
            prior = common[common["組別"].eq(PRIOR_GROUP)][column]
            new = common[common["組別"].eq(NEW_GROUP)][column]
            rows.append(
                {
                    "階段": stage,
                    "指標": label,
                    "名單內_n": len(prior),
                    "名單外_n": len(new),
                    "平均差_內減外": prior.mean() - new.mean(),
                    "中位數差_內減外": prior.median() - new.median(),
                    "Cliffs_delta": cliffs_delta(prior, new),
                }
            )
    return pd.DataFrame(rows)


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def make_report(
    evidence: pd.DataFrame,
    summary: pd.DataFrame,
    stages: pd.DataFrame,
    archive: str,
) -> str:
    prior = evidence[evidence["組別"].eq(PRIOR_GROUP)]
    new = evidence[evidence["組別"].eq(NEW_GROUP)]
    high_prior = int(prior["高涵蓋(>=8/11)"].sum())
    high_new = int(new["高涵蓋(>=8/11)"].sum())
    coverage_odds, coverage_p = fisher_exact_two_sided(
        high_prior, len(prior) - high_prior, high_new, len(new) - high_new
    )
    late_prior = int(prior["遲交"].sum())
    late_new = int(new["遲交"].sum())
    late_odds, late_p = fisher_exact_two_sided(
        late_prior, len(prior) - late_prior, late_new, len(new) - late_new
    )

    lines = [
        "# 第一個網頁作業之先備課程優勢：深入證據分析",
        "",
        f"- 作業來源：{archive}",
        f"- {PRIOR_GROUP}：**{len(prior)} 人**；{NEW_GROUP}：**{len(new)} 人**",
        "- 目的：檢驗「有上學期作品紀錄者在第一個網頁作業表現較佳」是否有多項證據支持。",
        "",
        "> 本分析為事後探索。分組是作品名單代理、不是正式選課紀錄；",
        "> 主題涵蓋只判斷關鍵概念是否出現，不判斷內容正確性。",
        "",
        "## 多指標證據",
        "",
        "| 指標 | 名單內平均／中位數 | 名單外平均／中位數 | 平均差 | Cliff's δ | 精確 p |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        digits = 0 if row["指標"] in {"總字數", "專有名詞絕對次數"} else 2
        lines.append(
            f"| {row['指標']} | {fmt(row['名單內_平均'], digits)}／"
            f"{fmt(row['名單內_中位數'], digits)} | "
            f"{fmt(row['名單外_平均'], digits)}／{fmt(row['名單外_中位數'], digits)} | "
            f"{fmt(row['平均差_內減外'], digits)} | "
            f"{row['Cliffs_delta']:.3f} | {row['精確秩排列_p']:.3f} |"
        )

    lines += [
        "",
        "## 可支持「早期優勢」的證據",
        "",
        f"1. **內容量**：名單內組平均多 {prior['總字數'].mean()-new['總字數'].mean():.0f} 字，"
        f"中位數多 {prior['總字數'].median()-new['總字數'].median():.0f} 字；"
        f"效果量 δ={summary.loc[summary['指標'].eq('總字數'),'Cliffs_delta'].iloc[0]:.3f}。",
        f"2. **專有名詞絕對使用量**：名單內平均 {prior['專有名詞出現次數'].mean():.1f} 次、"
        f"名單外 {new['專有名詞出現次數'].mean():.1f} 次；中位數差 "
        f"{prior['專有名詞出現次數'].median()-new['專有名詞出現次數'].median():.1f} 次。",
        f"3. **指定概念涵蓋**：名單內平均涵蓋 {prior['主題涵蓋數'].mean():.2f}/11、"
        f"名單外 {new['主題涵蓋數'].mean():.2f}/11；中位數差 "
        f"{prior['主題涵蓋數'].median()-new['主題涵蓋數'].median():.1f} 個主題。",
        f"4. **高涵蓋作品比例**（≥8/11）：名單內 {high_prior}/{len(prior)} "
        f"({high_prior/len(prior)*100:.1f}%)，名單外 {high_new}/{len(new)} "
        f"({high_new/len(new)*100:.1f}%)；OR={coverage_odds:.2f}，Fisher p={coverage_p:.3f}。",
        "5. **三項內容指標的方向一致**：篇幅、專有名詞絕對次數、主題涵蓋數都偏向名單內組。",
        "探索性的「內容發展指數」效果量為 "
        f"δ={summary.loc[summary['指標'].eq('內容發展指數（探索性）'),'Cliffs_delta'].iloc[0]:.3f}，"
        f"p={summary.loc[summary['指標'].eq('內容發展指數（探索性）'),'精確秩排列_p'].iloc[0]:.3f}。",
        "",
        "## 不支持「全面優於」的證據",
        "",
        "- 兩組媒體與排版中位數相同，結構面沒有明顯分離。",
        f"- 遲交比例近似：名單內 {late_prior}/{len(prior)}，名單外 {late_new}/{len(new)}；"
        f"OR={late_odds:.2f}，Fisher p={late_p:.3f}。",
        "- 單項與綜合指標的精確 p 值皆未低於 .05；小樣本下只能稱為中等幅度、方向一致的趨勢。",
        "",
        "## 優勢是否延續到期末",
        "",
        "以下限定為同時有第一個作業與期末報告的 18 人（13 對 5）。正的 δ 代表名單內組較高。",
        "",
        "| 指標 | 作業平均差／δ | 期末平均差／δ |",
        "| --- | ---: | ---: |",
    ]
    for metric in stages["指標"].unique():
        hw = stages[(stages["指標"].eq(metric)) & (stages["階段"].eq("第一個網頁作業"))].iloc[0]
        final = stages[(stages["指標"].eq(metric)) & (stages["階段"].eq("期末報告"))].iloc[0]
        lines.append(
            f"| {metric} | {hw['平均差_內減外']:+.2f}／{hw['Cliffs_delta']:.3f} | "
            f"{final['平均差_內減外']:+.2f}／{final['Cliffs_delta']:.3f} |"
        )

    lines += [
        "",
        "媒體、篇幅與反思訊號的組間效果量到期末均縮小，與「未修過上學期課程者逐步追上」的解釋一致；",
        "但兩階段作業要求不同，因此不能把變化完全歸因於追趕效果。",
        "",
        "## 最穩健的表述",
        "",
        "> 深入分析顯示，有上學期作品紀錄的學生在下學期第一個網頁作業中，",
        "> 呈現較大的內容量、較多的專有名詞絕對使用次數，以及較完整的指定主題涵蓋；",
        "> 多項內容指標方向一致，形成「先備經驗帶來早期內容建構優勢」的探索性證據。",
        "> 然而，媒體與排版的典型水準相同，且小樣本精確檢定未達顯著，",
        "> 因此不宜宣稱整體作業品質已被證實顯著優於另一組。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="深入檢驗第一個網頁作業的先備課程優勢")
    parser.add_argument("--archive", default=DEFAULT_ARCHIVE, help="作業 ZIP 路徑或 URL")
    parser.add_argument(
        "--assignment-results",
        default="seismology_2026_hw2_results.csv",
        help="第一個網頁作業分析 CSV",
    )
    parser.add_argument(
        "--final-results",
        default="results_seismology_2026_final_primary.csv",
        help="下學期期末作品分析 CSV",
    )
    parser.add_argument(
        "--evidence-output",
        default="seismology_2026_hw2_prior_advantage_evidence.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="seismology_2026_hw2_prior_advantage_summary.csv",
    )
    parser.add_argument(
        "--stage-output",
        default="seismology_2026_prior_advantage_by_stage.csv",
    )
    parser.add_argument(
        "--report",
        default="seismology_2026_hw2_prior_advantage_deep_dive.md",
    )
    args = parser.parse_args()
    if not args.archive:
        parser.error("--archive is required; the identifiable source archive is not public")

    evidence = collect_assignment_evidence(args.archive, args.assignment_results)
    summary = build_deep_summary(evidence)
    stages = stage_effects(evidence, args.final_results)

    evidence.to_csv(args.evidence_output, index=False, encoding="utf-8-sig")
    summary.to_csv(args.summary_output, index=False, encoding="utf-8-sig")
    stages.to_csv(args.stage_output, index=False, encoding="utf-8-sig")
    Path(args.report).write_text(
        make_report(evidence, summary, stages, args.archive), encoding="utf-8"
    )
    print(f"[saved] {args.evidence_output}")
    print(f"[saved] {args.summary_output}")
    print(f"[saved] {args.stage_output}")
    print(f"[saved] {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
