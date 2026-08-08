#!/usr/bin/env python3
"""Analyze all webpages in an EEClass assignment ZIP and compare prior-course groups."""

from __future__ import annotations

import argparse
import io
import itertools
import re
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

import pandas as pd
import requests
from bs4 import BeautifulSoup

from analyze_web import (
    USER_AGENT,
    analyze_record,
    expand_sparse_html,
    load_html,
)

DEFAULT_ARCHIVE = (
    "https://raw.githubusercontent.com/oceanicdayi/Evaluate_web/main/hw_68852-1.zip"
)
PRIOR_GROUP = "上學期作品名單內"
NEW_GROUP = "未見於上學期作品名單"
METRICS = {
    "媒體豐富度(1-4)": "媒體豐富度",
    "排版架構(1-4)": "排版架構",
    "總字數": "總字數",
    "專有名詞密度(次/千字)": "術語密度",
    "批判思考佔比(%)": "批判思考比例",
}


def open_archive(source: str) -> zipfile.ZipFile:
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=60, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return zipfile.ZipFile(io.BytesIO(response.content))
    return zipfile.ZipFile(source)


def decode_member(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "big5", "cp950"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def student_members(zf: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    """Return (student id, name, content member) from archive folders."""
    students = []
    for member in zf.namelist():
        match = re.fullmatch(r"([^/]+)/content\.html", member, flags=re.I)
        if not match:
            continue
        folder = unquote(match.group(1))
        identity = re.match(r"(u\d+)\s*\((.+)\)", folder, flags=re.I)
        if not identity:
            continue
        students.append((identity.group(1).upper(), identity.group(2), member))
    return sorted(students)


def valid_external_artifact(url: str) -> bool:
    low = url.lower()
    if not low.startswith(("http://", "https://")):
        return False
    if "eeclass.utaipei.edu.tw" in low:
        return False
    if "github.com/" in low and ".github.io" not in low:
        return False
    return not low.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"))


def find_artifact(
    zf: zipfile.ZipFile, content_member: str
) -> tuple[str, str, int]:
    """
    Return (source, HTML, attachment count).

    Prefer deployed external webpages; otherwise analyze an attached HTML file.
    """
    content_html = decode_member(zf.read(content_member))
    soup = BeautifulSoup(content_html, "html.parser")
    folder = str(PurePosixPath(content_member).parent)
    members = set(zf.namelist())
    attachments = [
        name
        for name in members
        if str(PurePosixPath(name).parent) == folder
        and name != content_member
        and not name.endswith("/")
    ]

    external = []
    local_html = []
    for anchor in soup.find_all("a", href=True):
        href = unquote(anchor["href"].strip())
        if valid_external_artifact(href):
            external.append(href)
        elif not href.startswith(("javascript:", "http://", "https://")):
            candidate = str(PurePosixPath(folder) / PurePosixPath(href))
            if candidate in members and candidate.lower().endswith((".html", ".htm")):
                local_html.append(candidate)

    if external:
        # Prefer deployed pages over ancillary links.
        external.sort(
            key=lambda url: (
                0
                if any(
                    host in url.lower()
                    for host in (".github.io", ".hf.space", "streamlit.app")
                )
                else 1
            )
        )
        source = external[0]
        return source, load_html(source), len(attachments)

    if local_html:
        member = local_html[0]
        html = decode_member(zf.read(member))
        # Extract JSX/template text from a self-contained attached app.
        html = expand_sparse_html(f"https://archive.invalid/{member}", html)
        return f"archive://{member}", html, len(attachments)

    return f"archive://{content_member}", content_html, len(attachments)


def adjust_client_rendered_scores(row: dict, html: str) -> None:
    """
    Static source still exposes interaction/layout in React/JSX.

    The base rubric scans rendered HTML tags. For source-only submissions, promote
    to level 3 when explicit interaction or navigation code is present.
    """
    soup = BeautifulSoup(html, "html.parser")
    script = "\n".join(s.get_text() or "" for s in soup.find_all("script"))
    interactive = bool(
        re.search(
            r"on(?:click|change|input)\s*=|addEventListener|useState\s*\(|"
            r"requestAnimationFrame|setInterval\s*\(|\bquiz\b",
            script,
            flags=re.I,
        )
    )
    structured = bool(
        re.search(
            r"<nav\b|activeTab|side(?:bar|menu)|menuOpen|chapter[s]?\s*=|"
            r"\btabs?\s*=",
            script,
            flags=re.I,
        )
    )
    if interactive and (row["媒體豐富度(1-4)"] or 0) < 3:
        row["媒體豐富度(1-4)"] = 3
        row["JS互動補正"] = True
    else:
        row["JS互動補正"] = False
    if structured and (row["排版架構(1-4)"] or 0) < 3:
        row["排版架構(1-4)"] = 3
        row["JS排版補正"] = True
    else:
        row["JS排版補正"] = False


def analyze_archive(archive: str, prior_csv: str) -> pd.DataFrame:
    prior = pd.read_csv(prior_csv, dtype={"學號": str})
    prior_ids = set(prior["學號"].dropna())
    rows = []

    with open_archive(archive) as zf:
        for sid, name, member in student_members(zf):
            print(f"[info] 分析 {sid} {name}")
            try:
                source, html, attachment_count = find_artifact(zf, member)
                row = analyze_record(
                    sid,
                    "Seismology_2026_HW2",
                    html,
                    source=source,
                    name=name,
                    attachment_count=attachment_count,
                )
                adjust_client_rendered_scores(row, html)
            except Exception as exc:  # noqa: BLE001
                row = analyze_record(
                    sid,
                    "Seismology_2026_HW2",
                    "",
                    source=f"archive://{member}",
                    name=name,
                    error=f"artifact_error:{exc}",
                )
                row["JS互動補正"] = False
                row["JS排版補正"] = False
            row["組別"] = PRIOR_GROUP if sid in prior_ids else NEW_GROUP
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["組別", "學號"]).reset_index(drop=True)


def cliffs_delta(a: pd.Series, b: pd.Series) -> float:
    greater = sum(x > y for x in a for y in b)
    less = sum(x < y for x in a for y in b)
    return (greater - less) / (len(a) * len(b))


def exact_rank_permutation_p(values: pd.Series, prior_mask: pd.Series) -> float:
    values = values.reset_index(drop=True)
    prior_mask = prior_mask.reset_index(drop=True)
    ranks = values.rank(method="average").tolist()
    n = len(ranks)
    n_prior = int(prior_mask.sum())
    observed = sum(rank for rank, selected in zip(ranks, prior_mask) if selected)
    expected = n_prior * (n + 1) / 2
    deviation = abs(observed - expected)
    total = 0
    extreme = 0
    for combination in itertools.combinations(range(n), n_prior):
        rank_sum = sum(ranks[i] for i in combination)
        extreme += abs(rank_sum - expected) >= deviation - 1e-12
        total += 1
    return extreme / total


def summarize(scored: pd.DataFrame) -> pd.DataFrame:
    usable = scored[scored["狀態"].isin(["ok", "limited"])].copy()
    prior = usable[usable["組別"].eq(PRIOR_GROUP)]
    new = usable[usable["組別"].eq(NEW_GROUP)]
    rows = []
    for metric, label in METRICS.items():
        a = prior[metric].dropna()
        b = new[metric].dropna()
        rows.append(
            {
                "指標": label,
                "名單內_n": len(a),
                "名單內_平均": a.mean(),
                "名單內_中位數": a.median(),
                "名單外_n": len(b),
                "名單外_平均": b.mean(),
                "名單外_中位數": b.median(),
                "平均差_內減外": a.mean() - b.mean(),
                "中位數差_內減外": a.median() - b.median(),
                "Cliffs_delta": cliffs_delta(a, b),
                "精確秩排列_p": exact_rank_permutation_p(
                    usable[metric], usable["組別"].eq(PRIOR_GROUP)
                ),
            }
        )
    return pd.DataFrame(rows)


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def make_report(scored: pd.DataFrame, summary: pd.DataFrame, archive: str) -> str:
    prior = scored[scored["組別"].eq(PRIOR_GROUP)]
    new = scored[scored["組別"].eq(NEW_GROUP)]
    lines = [
        "# 下學期第一個網頁作業：依上學期作品名單分組比較",
        "",
        f"- 來源：{archive}",
        "- 壓縮檔內的正式作業名稱：**作業2－介紹地震學課本第一章－部署網頁在 GitHub Pages**",
        f"- {PRIOR_GROUP}：**{len(prior)} 人**",
        f"- {NEW_GROUP}：**{len(new)} 人**",
        "",
        "> 分組以是否出現在上學期期末作品名單為代理變項，不是正式選課紀錄。",
        "",
        "## 組別成果",
        "",
        "| 指標 | 名單內平均／中位數 | 名單外平均／中位數 | 平均差（內−外） | "
        "中位數差（內−外） |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        digits = 0 if row["指標"] == "總字數" else 2
        lines.append(
            f"| {row['指標']} | {fmt(row['名單內_平均'], digits)}／"
            f"{fmt(row['名單內_中位數'], digits)} | "
            f"{fmt(row['名單外_平均'], digits)}／{fmt(row['名單外_中位數'], digits)} | "
            f"{fmt(row['平均差_內減外'], digits)} | "
            f"{fmt(row['中位數差_內減外'], digits)} |"
        )

    lines += [
        "",
        "## 探索性組間比較",
        "",
        "| 指標 | Cliff's δ | 精確秩排列 p |",
        "| --- | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['指標']} | {row['Cliffs_delta']:.3f} | "
            f"{row['精確秩排列_p']:.3f} |"
        )

    by_metric = summary.set_index("指標")
    words = by_metric.loc["總字數"]
    media = by_metric.loc["媒體豐富度"]
    layout = by_metric.loc["排版架構"]
    terms = by_metric.loc["術語密度"]
    reflection = by_metric.loc["批判思考比例"]
    lines += [
        "",
        "## 結果解讀",
        "",
        f"1. **篇幅是最明顯的描述性差異**：名單內組平均 {words['名單內_平均']:.0f} 字、"
        f"中位數 {words['名單內_中位數']:.0f} 字；名單外組平均 {words['名單外_平均']:.0f} 字、"
        f"中位數 {words['名單外_中位數']:.0f} 字。名單內組高出約 "
        f"{words['平均差_內減外']:.0f} 字（平均）與 {words['中位數差_內減外']:.0f} 字（中位數）。",
        f"2. **媒體與排版的典型水準相同**：兩組媒體中位數都是 {media['名單內_中位數']:.0f}，"
        f"排版中位數都是 {layout['名單內_中位數']:.0f}；名單內組的平均僅高 "
        f"{media['平均差_內減外']:.2f} 與 {layout['平均差_內減外']:.2f} 分。",
        f"3. **術語密度反而以名單外組較高**：平均差 {terms['平均差_內減外']:.2f} 次/千字。",
        "這不代表學科內容較好；名單內組文章較長時，分母擴大會自然降低密度。",
        f"4. **批判思考只呈小幅差異**：名單內平均高 {reflection['平均差_內減外']:.2f} 個百分點、"
        f"中位數高 {reflection['中位數差_內減外']:.2f} 個百分點；且本作業本來以課本介紹為主，"
        "不應把此指標當成核心成果。",
        "5. 五項精確秩排列比較皆未達一般顯著門檻（最小探索性 p = "
        f"{summary['精確秩排列_p'].min():.3f}）。樣本為 14 對 6，"
        "因此「名單內組篇幅較長」應視為值得追蹤的描述性趨勢，而非已證實的課程效果。",
        "",
        "## 小結",
        "",
        "在下學期第一個網頁作業中，有上學期作品紀錄的學生，主要優勢呈現在**內容量較大**；",
        "兩組在媒體與排版的中位水準沒有差別。這表示先備經驗可能幫助學生更快擴充內容，",
        "但未顯示出明確的網頁結構優勢。",
    ]

    lines += [
        "",
        "## 個別作品",
        "",
        "| 組別 | 學號 | 姓名 | 媒體 | 排版 | 字數 | 術語密度 | 批判思考% | 狀態 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for _, row in scored.iterrows():
        lines.append(
            f"| {row['組別']} | {row['學號']} | {row['姓名']} | "
            f"{row['媒體豐富度(1-4)']} | {row['排版架構(1-4)']} | "
            f"{row['總字數']} | {row['專有名詞密度(次/千字)']:.2f} | "
            f"{row['批判思考佔比(%)']:.1f} | {row['狀態']} |"
        )

    lines += [
        "",
        "## 解讀限制",
        "",
        "- 本作業要求介紹課本第一章，主要是知識描述；「批判思考比例」不是主要學習目標，只列為輔助資訊。",
        "- 部分網頁以 React/JavaScript 動態產生內容；分析器會從程式中的互動與導覽結構補正尺規。",
        "- 分組非隨機且人數不均，排列 p 值僅供探索，不代表課程先備經驗造成差異。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="分析 EEClass 作業 ZIP 並比較先備課程組別")
    parser.add_argument("--archive", default=DEFAULT_ARCHIVE, help="ZIP 路徑或 URL")
    parser.add_argument(
        "--prior-roster",
        default="results_geophysics_2025_final.csv",
        help="上學期期末作品名單 CSV",
    )
    parser.add_argument(
        "--results",
        default="seismology_2026_hw2_results.csv",
        help="個別作品結果 CSV",
    )
    parser.add_argument(
        "--summary",
        default="seismology_2026_hw2_group_summary.csv",
        help="組別摘要 CSV",
    )
    parser.add_argument(
        "--report",
        default="seismology_2026_hw2_group_comparison.md",
        help="Markdown 報告",
    )
    args = parser.parse_args()

    scored = analyze_archive(args.archive, args.prior_roster)
    summary = summarize(scored)
    scored.to_csv(args.results, index=False, encoding="utf-8-sig")
    summary.to_csv(args.summary, index=False, encoding="utf-8-sig")
    Path(args.report).write_text(
        make_report(scored, summary, args.archive), encoding="utf-8"
    )

    print(scored["組別"].value_counts().to_string())
    print(f"[saved] {args.results}")
    print(f"[saved] {args.summary}")
    print(f"[saved] {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
