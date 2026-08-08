#!/usr/bin/env python3
"""Generate Figure 1 and Figure 2 as publication-ready SVG files."""

from __future__ import annotations

import html
from pathlib import Path

import cairosvg
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "longitudinal_comparison_2025_2026_high_confidence.csv"

INK = "#123137"
MUTED = "#617477"
GRID = "#d9d5ca"
PAPER = "#fbf8ef"
UPPER = "#e66f5b"
LOWER = "#159e94"
GOLD = "#d7aa4b"
FONT = "system-ui,-apple-system,'Segoe UI','Noto Sans TC',sans-serif"


def esc(value) -> str:
    return html.escape(str(value))


def figure1(data: pd.DataFrame) -> str:
    width, height = 1400, 760
    panels = [
        ("媒體豐富度", "媒體豐富度(1-4)", 90),
        ("排版架構", "排版架構(1-4)", 750),
    ]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">圖一：學生網頁作品複雜度上下學期評分分布</title>',
        '<desc id="desc">高信度配對八位學生的媒體豐富度與排版架構一至四分分布。媒體分數明顯向四分移動，排版大致維持三分。</desc>',
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        f'<text x="70" y="70" fill="{INK}" font-family="{FONT}" font-size="34" font-weight="800">圖一　學生網頁作品複雜度評分分布</text>',
        f'<text x="70" y="108" fill="{MUTED}" font-family="{FONT}" font-size="18">同一批高信度配對學生（n=8）｜上學期：地球物理通論；下學期：地震學</text>',
        f'<circle cx="1035" cy="72" r="8" fill="{UPPER}"/><text x="1052" y="79" fill="{INK}" font-family="{FONT}" font-size="16">上學期</text>',
        f'<circle cx="1160" cy="72" r="8" fill="{LOWER}"/><text x="1177" y="79" fill="{INK}" font-family="{FONT}" font-size="16">下學期</text>',
    ]
    panel_w = 570
    plot_top, plot_bottom = 205, 610
    plot_h = plot_bottom - plot_top
    max_count = 8
    for title, metric, left in panels:
        plot_left = left + 70
        plot_right = left + panel_w - 25
        plot_w = plot_right - plot_left
        svg += [
            f'<rect x="{left}" y="145" width="{panel_w}" height="535" rx="20" fill="#ffffff" stroke="#ded9cc"/>',
            f'<text x="{left + 28}" y="190" fill="{INK}" font-family="{FONT}" font-size="24" font-weight="750">{title}</text>',
        ]
        for tick in range(0, max_count + 1, 2):
            y = plot_bottom - (tick / max_count) * plot_h
            svg.append(
                f'<line x1="{plot_left}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
            )
            svg.append(
                f'<text x="{plot_left - 15}" y="{y + 6:.1f}" text-anchor="end" fill="{MUTED}" font-family="{FONT}" font-size="14">{tick}</text>'
            )
        svg.append(
            f'<text x="{left + 23}" y="{(plot_top + plot_bottom) / 2}" transform="rotate(-90 {left + 23} {(plot_top + plot_bottom) / 2})" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="14">學生人數</text>'
        )
        upper_counts = (
            data[f"{metric}_上學期"].value_counts().reindex([1, 2, 3, 4], fill_value=0)
        )
        lower_counts = (
            data[f"{metric}_下學期"].value_counts().reindex([1, 2, 3, 4], fill_value=0)
        )
        group_w = plot_w / 4
        bar_w = 34
        for i, score in enumerate([1, 2, 3, 4]):
            cx = plot_left + group_w * (i + 0.5)
            for value, color, offset in (
                (int(upper_counts[score]), UPPER, -bar_w - 3),
                (int(lower_counts[score]), LOWER, 3),
            ):
                bar_h = value / max_count * plot_h
                x = cx + offset
                y = plot_bottom - bar_h
                svg.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="5" fill="{color}"/>'
                )
                if value:
                    svg.append(
                        f'<text x="{x + bar_w / 2:.1f}" y="{y - 9:.1f}" text-anchor="middle" fill="{INK}" font-family="{FONT}" font-size="15" font-weight="700">{value}</text>'
                    )
            svg.append(
                f'<text x="{cx:.1f}" y="{plot_bottom + 31}" text-anchor="middle" fill="{INK}" font-family="{FONT}" font-size="16">{score} 分</text>'
            )
        note = (
            "下學期 6/8 達到 4 分"
            if metric == "媒體豐富度(1-4)"
            else "兩學期皆以 3 分為主"
        )
        svg.append(
            f'<text x="{left + panel_w / 2}" y="660" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="15">{note}</text>'
        )
    svg += [
        f'<text x="70" y="725" fill="{MUTED}" font-family="{FONT}" font-size="15">註：1–4 分為序位尺規；本圖僅納入兩學期網頁皆可完整讀取的配對學生。</text>',
        "</svg>",
    ]
    return "\n".join(svg)


def figure2(data: pd.DataFrame) -> str:
    width, height = 1400, 840
    left, right, top, bottom = 120, 1310, 145, 720
    plot_w, plot_h = right - left, bottom - top
    x_max, y_max = 55, 35

    def sx(value: float) -> float:
        return left + value / x_max * plot_w

    def sy(value: float) -> float:
        return bottom - value / y_max * plot_h

    label_offsets = {
        "陳亞歆": (10, -8),
        "邱定軒": (10, -12),
        "楊廂甯": (10, 20),
        "李政暟": (10, 18),
        "張智詠": (10, -8),
        "陳柏亘": (10, 19),
        "林靖融": (10, -10),
        "洪敏書": (10, 18),
    }
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">圖二：專有名詞密度與批判思考比例之跨學期位移</title>',
        '<desc id="desc">八位配對學生從上學期到下學期在專有名詞密度與批判思考比例散布圖上的移動。箭頭由上學期指向下學期。</desc>',
        f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker><marker id="mean-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GOLD}"/></marker></defs>',
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        f'<text x="70" y="62" fill="{INK}" font-family="{FONT}" font-size="34" font-weight="800">圖二　文本分析指標的跨學期位移</text>',
        f'<text x="70" y="101" fill="{MUTED}" font-family="{FONT}" font-size="18">箭頭由上學期指向下學期｜高信度配對學生 n=8</text>',
    ]
    for tick in range(0, 56, 5):
        x = sx(tick)
        svg.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{GRID}" stroke-width="1"/>'
        )
        if tick % 10 == 0:
            svg.append(
                f'<text x="{x:.1f}" y="{bottom + 30}" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="14">{tick}</text>'
            )
    for tick in range(0, 36, 5):
        y = sy(tick)
        svg.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{left - 16}" y="{y + 5:.1f}" text-anchor="end" fill="{MUTED}" font-family="{FONT}" font-size="14">{tick}</text>'
        )
    svg += [
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="{INK}" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="{INK}" stroke-width="2"/>',
        f'<text x="{(left + right) / 2}" y="785" text-anchor="middle" fill="{INK}" font-family="{FONT}" font-size="18" font-weight="700">專有名詞密度（次／千字）</text>',
        f'<text x="38" y="{(top + bottom) / 2}" transform="rotate(-90 38 {(top + bottom) / 2})" text-anchor="middle" fill="{INK}" font-family="{FONT}" font-size="18" font-weight="700">批判思考比例（%）</text>',
    ]
    for _, row in data.iterrows():
        name = str(row["姓名"])
        ux = float(row["專有名詞密度(次/千字)_上學期"])
        uy = float(row["批判思考佔比(%)_上學期"])
        lx = float(row["專有名詞密度(次/千字)_下學期"])
        ly = float(row["批判思考佔比(%)_下學期"])
        svg += [
            f'<line x1="{sx(ux):.1f}" y1="{sy(uy):.1f}" x2="{sx(lx):.1f}" y2="{sy(ly):.1f}" stroke="{INK}" stroke-width="2" stroke-opacity=".48" marker-end="url(#arrow)"/>',
            f'<circle cx="{sx(ux):.1f}" cy="{sy(uy):.1f}" r="7" fill="{UPPER}" stroke="white" stroke-width="2"/>',
            f'<circle cx="{sx(lx):.1f}" cy="{sy(ly):.1f}" r="8" fill="{LOWER}" stroke="white" stroke-width="2"/>',
        ]
        dx, dy = label_offsets.get(name, (10, -8))
        svg.append(
            f'<text x="{sx(lx) + dx:.1f}" y="{sy(ly) + dy:.1f}" fill="{INK}" font-family="{FONT}" font-size="14" font-weight="650">{esc(name)}</text>'
        )
    mean_ux = data["專有名詞密度(次/千字)_上學期"].mean()
    mean_uy = data["批判思考佔比(%)_上學期"].mean()
    mean_lx = data["專有名詞密度(次/千字)_下學期"].mean()
    mean_ly = data["批判思考佔比(%)_下學期"].mean()
    svg += [
        f'<line x1="{sx(mean_ux):.1f}" y1="{sy(mean_uy):.1f}" x2="{sx(mean_lx):.1f}" y2="{sy(mean_ly):.1f}" stroke="{GOLD}" stroke-width="5" stroke-dasharray="8 6" marker-end="url(#mean-arrow)"/>',
        f'<rect x="{sx(mean_ux) - 7:.1f}" y="{sy(mean_uy) - 7:.1f}" width="14" height="14" transform="rotate(45 {sx(mean_ux):.1f} {sy(mean_uy):.1f})" fill="{GOLD}" stroke="white" stroke-width="2"/>',
        f'<rect x="{sx(mean_lx) - 8:.1f}" y="{sy(mean_ly) - 8:.1f}" width="16" height="16" transform="rotate(45 {sx(mean_lx):.1f} {sy(mean_ly):.1f})" fill="{GOLD}" stroke="white" stroke-width="2"/>',
        f'<text x="{sx(mean_lx) + 18:.1f}" y="{sy(mean_ly) - 14:.1f}" fill="#8a651d" font-family="{FONT}" font-size="14" font-weight="800">班級平均</text>',
        f'<circle cx="1020" cy="95" r="7" fill="{UPPER}"/><text x="1037" y="101" fill="{INK}" font-family="{FONT}" font-size="15">上學期</text>',
        f'<circle cx="1125" cy="95" r="7" fill="{LOWER}"/><text x="1142" y="101" fill="{INK}" font-family="{FONT}" font-size="15">下學期</text>',
        f'<rect x="1232" y="88" width="12" height="12" transform="rotate(45 1238 94)" fill="{GOLD}"/><text x="1255" y="101" fill="{INK}" font-family="{FONT}" font-size="15">平均</text>',
        f'<text x="70" y="822" fill="{MUTED}" font-family="{FONT}" font-size="14">註：批判思考比例為關鍵詞啟發式估計；未取得先備成績，故以配對箭頭呈現，未作高／低成就分群。</text>',
        "</svg>",
    ]
    return "\n".join(svg)


def main() -> int:
    data = pd.read_csv(DATA)
    figure1_svg = figure1(data)
    figure2_svg = figure2(data)
    (ROOT / "figure1_web_complexity_distribution.svg").write_text(
        figure1_svg, encoding="utf-8"
    )
    (ROOT / "figure2_text_analytics_trajectory.svg").write_text(
        figure2_svg, encoding="utf-8"
    )
    cairosvg.svg2png(
        bytestring=figure1_svg.encode("utf-8"),
        write_to=str(ROOT / "figure1_web_complexity_distribution.png"),
        output_width=2800,
        output_height=1520,
    )
    cairosvg.svg2png(
        bytestring=figure2_svg.encode("utf-8"),
        write_to=str(ROOT / "figure2_text_analytics_trajectory.png"),
        output_width=2800,
        output_height=1680,
    )
    print("[saved] figure1_web_complexity_distribution.svg")
    print("[saved] figure1_web_complexity_distribution.png (2800×1520)")
    print("[saved] figure2_text_analytics_trajectory.svg")
    print("[saved] figure2_text_analytics_trajectory.png (2800×1680)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
