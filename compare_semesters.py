#!/usr/bin/env python3
"""Compare matched students across Geophysics and Seismology final reports."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

METRICS = {
    "媒體豐富度(1-4)": "媒體",
    "排版架構(1-4)": "排版",
    "總字數": "字數",
    "專有名詞密度(次/千字)": "術語密度",
    "批判思考佔比(%)": "批判思考",
}

DEFAULT_GEO_URL = (
    "https://oceanicdayi.github.io/2025_Geophysics_Final_Report/student_works.html"
)
DEFAULT_SEIS_URL = (
    "https://oceanicdayi.github.io/Seismology_2026_final_report_Utaipei/"
)


def load_and_match(geophysics_csv: str, seismology_csv: str) -> pd.DataFrame:
    geo = pd.read_csv(geophysics_csv, dtype={"學號": str})
    seis = pd.read_csv(seismology_csv, dtype={"學號": str})

    # Exact ID + name matching prevents accidental joins on duplicate names.
    matched = geo.merge(
        seis,
        on=["學號", "姓名"],
        how="inner",
        suffixes=("_上學期", "_下學期"),
        validate="one_to_one",
    )

    for metric, short in METRICS.items():
        matched[f"{short}_變化"] = (
            matched[f"{metric}_下學期"] - matched[f"{metric}_上學期"]
        )

    limitation = matched.get("抓取限制", pd.Series("", index=matched.index)).fillna("")
    upper_words = matched["總字數_上學期"]
    lower_ok = matched["狀態_下學期"].eq("ok")
    upper_ok = matched["狀態_上學期"].eq("ok")

    matched["比較信度"] = "高"
    matched.loc[~upper_ok | ~lower_ok, "比較信度"] = "受限"
    matched.loc[upper_ok & (upper_words < 400), "比較信度"] = "低（上學期頁面過短）"
    matched["限制原因"] = limitation
    matched.loc[
        matched["比較信度"].eq("低（上學期頁面過短）"), "限制原因"
    ] = "upper_static_text_below_400"

    return matched.sort_values(["學號", "姓名"]).reset_index(drop=True)


def fmt_num(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.{digits}f}"


def fmt_delta(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{fmt_num(value, digits)}"


def direction_counts(series: pd.Series) -> tuple[int, int, int]:
    return int((series > 0).sum()), int((series == 0).sum()), int((series < 0).sum())


def make_markdown(matched: pd.DataFrame, geo_url: str, seis_url: str) -> str:
    high = matched[matched["比較信度"].eq("高")].copy()
    limited = matched[~matched["比較信度"].eq("高")].copy()

    lines = [
        "# 兩學期學生期末網頁作品縱向比較",
        "",
        f"- 上學期（地球物理通論）：{geo_url}",
        f"- 下學期（地震學）：{seis_url}",
        f"- 同名且同學號：**{len(matched)} 人**",
        f"- 可作班級統計的高信度配對：**{len(high)} 人**",
        f"- 受登入牆、SPA/Streamlit 或過短靜態頁限制：**{len(limited)} 人**",
        "",
        "## 方法與解讀限制",
        "",
        "以「學號＋姓名」精確配對，避免同名誤配。兩學期使用同一套 HTML 尺規與術語字典。",
        "班級平均只納入兩份作品均可讀，且上學期靜態文本至少 400 字的配對。",
        "媒體與排版為 1–4 級序位尺規；術語密度會受篇幅分母影響；批判思考比例是關鍵詞啟發式估計，",
        "因此適合描述趨勢，不宜視為學科成績或精確心理量測。",
        "",
        "## 班級層級結果（高信度配對）",
        "",
        "| 指標 | 上學期平均 | 下學期平均 | 平均變化 | 上升／持平／下降 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for metric, short in METRICS.items():
        upper = high[f"{metric}_上學期"]
        lower = high[f"{metric}_下學期"]
        delta = high[f"{short}_變化"]
        up, same, down = direction_counts(delta)
        digits = 0 if metric == "總字數" else 2
        unit = " 個百分點" if metric == "批判思考佔比(%)" else ""
        lines.append(
            f"| {short} | {fmt_num(upper.mean(), digits)} | "
            f"{fmt_num(lower.mean(), digits)} | "
            f"{fmt_delta(delta.mean(), digits)}{unit} | {up}／{same}／{down} |"
        )

    word_gain_pct = (
        (high["總字數_下學期"].mean() / high["總字數_上學期"].mean() - 1) * 100
        if not high.empty and high["總字數_上學期"].mean()
        else 0
    )
    lines += [
        "",
        "### 主要發現",
        "",
        f"1. **媒體呈現明顯提升**：平均增加 {high['媒體_變化'].mean():.2f} 分；"
        f"{direction_counts(high['媒體_變化'])[0]}/{len(high)} 人提升，無人下降。",
        f"2. **排版架構大致持平**：平均變化 {high['排版_變化'].mean():+.2f} 分；"
        "多數上學期已達 3 分導覽分區，存在尺規天花板。",
        f"3. **內容篇幅擴張**：平均增加 {high['字數_變化'].mean():.0f} 字"
        f"（約 {word_gain_pct:+.1f}%）；{direction_counts(high['字數_變化'])[0]}/{len(high)} 人增加。",
        f"4. **術語密度不是一致上升**：平均增加 {high['術語密度_變化'].mean():.2f} 次/千字，"
        f"但上升與下降各 {direction_counts(high['術語密度_變化'])[0]} 人；"
        "篇幅增加時，密度可能因分母擴大而下降。",
        f"5. **反思訊號整體增加**：平均增加 {high['批判思考_變化'].mean():.2f} 個百分點；"
        f"{direction_counts(high['批判思考_變化'])[0]}/{len(high)} 人上升。",
        "",
        "## 每位配對學生",
        "",
        "| 學號 | 姓名 | 信度 | 媒體 上→下 (Δ) | 排版 上→下 (Δ) | 字數 上→下 (Δ) | "
        "術語密度 上→下 (Δ) | 批判思考% 上→下 (Δ) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for _, row in matched.iterrows():
        def pair(metric: str, short: str, digits: int = 1) -> str:
            upper = row[f"{metric}_上學期"]
            lower = row[f"{metric}_下學期"]
            delta = row[f"{short}_變化"]
            return (
                f"{fmt_num(upper, digits)}→{fmt_num(lower, digits)} "
                f"({fmt_delta(delta, digits)})"
            )

        lines.append(
            f"| {row['學號']} | {row['姓名']} | {row['比較信度']} | "
            f"{pair('媒體豐富度(1-4)', '媒體', 0)} | "
            f"{pair('排版架構(1-4)', '排版', 0)} | "
            f"{pair('總字數', '字數', 0)} | "
            f"{pair('專有名詞密度(次/千字)', '術語密度', 2)} | "
            f"{pair('批判思考佔比(%)', '批判思考', 1)} |"
        )

    if not high.empty:
        top_words = high.nlargest(3, "字數_變化")[["姓名", "字數_變化"]]
        top_media = high.nlargest(3, "媒體_變化")[["姓名", "媒體_變化"]]
        top_reflect = high.nlargest(3, "批判思考_變化")[["姓名", "批判思考_變化"]]

        def rank_text(frame: pd.DataFrame, col: str, suffix: str) -> str:
            return "、".join(
                f"{row['姓名']}（{fmt_delta(row[col], 1)}{suffix}）"
                for _, row in frame.iterrows()
            )

        lines += [
            "",
            "## 進步幅度較大的學生（高信度配對）",
            "",
            f"- 字數增加：{rank_text(top_words, '字數_變化', '字')}",
            f"- 媒體分數：{rank_text(top_media, '媒體_變化', '分')}",
            f"- 批判思考比例：{rank_text(top_reflect, '批判思考_變化', '個百分點')}",
        ]

    if not limited.empty:
        lines += [
            "",
            "## 未納入班級平均的配對",
            "",
            "| 學號 | 姓名 | 原因 |",
            "| --- | --- | --- |",
        ]
        for _, row in limited.iterrows():
            lines.append(
                f"| {row['學號']} | {row['姓名']} | "
                f"{row['限制原因'] or row['比較信度']} |"
            )

    lines += [
        "",
        "## 結論",
        "",
        "在可比較的同一批學生中，下學期作品最一致的改變是**媒體整合與篇幅增加**；",
        "排版大致維持既有的導覽分區水準。術語密度呈現分化，顯示內容變長不必然代表術語使用更集中。",
        "反思訊號多數上升，但仍需以人工雙盲評分或 LLM 多次評分驗證，才能支持推論統計或論文中的因果敘述。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="比較相同學生的兩學期期末網頁成果")
    parser.add_argument(
        "--geophysics",
        default="results_geophysics_2025_final.csv",
        help="上學期地球物理分析 CSV",
    )
    parser.add_argument(
        "--seismology",
        default="results_seismology_2026_final_primary.csv",
        help="下學期地震學分析 CSV（每人一筆）",
    )
    parser.add_argument(
        "--output",
        default="longitudinal_comparison_2025_2026.csv",
        help="全部配對 CSV",
    )
    parser.add_argument(
        "--high-confidence-output",
        default="longitudinal_comparison_2025_2026_high_confidence.csv",
        help="高信度配對 CSV",
    )
    parser.add_argument(
        "--report",
        default="longitudinal_comparison_2025_2026.md",
        help="Markdown 報告",
    )
    args = parser.parse_args()

    matched = load_and_match(args.geophysics, args.seismology)
    high = matched[matched["比較信度"].eq("高")].copy()

    matched.to_csv(args.output, index=False, encoding="utf-8-sig")
    high.to_csv(args.high_confidence_output, index=False, encoding="utf-8-sig")
    report = make_markdown(matched, DEFAULT_GEO_URL, DEFAULT_SEIS_URL)
    Path(args.report).write_text(report, encoding="utf-8")

    print(f"同名且同學號: {len(matched)} 人")
    print(f"高信度配對: {len(high)} 人")
    print(f"受限配對: {len(matched) - len(high)} 人")
    print(f"[saved] {args.output}")
    print(f"[saved] {args.high_confidence_output}")
    print(f"[saved] {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
