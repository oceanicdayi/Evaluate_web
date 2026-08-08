#!/usr/bin/env python3
"""Generate publication-ready longitudinal figures as SVG and PNG."""

from __future__ import annotations

import html
from pathlib import Path

import cairosvg
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "longitudinal_comparison_2025_2026_high_confidence.csv"
ASSIGNMENT_DATA = ROOT / "seismology_2026_hw2_prior_advantage_evidence.csv"
FINAL_DATA = ROOT / "results_seismology_2026_final_primary.csv"

INK = "#123137"
MUTED = "#617477"
GRID = "#d9d5ca"
PAPER = "#fbf8ef"
UPPER = "#e66f5b"
LOWER = "#159e94"
GOLD = "#d7aa4b"
FONT = "'Noto Sans CJK TC','Noto Sans TC','WenQuanYi Micro Hei',sans-serif"


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

    label_offsets = [(10, -9), (10, -12), (10, 20), (10, 18), (10, -8), (10, 19), (10, -10), (10, 18)]
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
    for index, (_, row) in enumerate(data.iterrows()):
        anonymous_id = str(row["匿名代碼"])
        ux = float(row["專有名詞密度(次/千字)_上學期"])
        uy = float(row["批判思考佔比(%)_上學期"])
        lx = float(row["專有名詞密度(次/千字)_下學期"])
        ly = float(row["批判思考佔比(%)_下學期"])
        svg += [
            f'<line x1="{sx(ux):.1f}" y1="{sy(uy):.1f}" x2="{sx(lx):.1f}" y2="{sy(ly):.1f}" stroke="{INK}" stroke-width="2" stroke-opacity=".48" marker-end="url(#arrow)"/>',
            f'<circle cx="{sx(ux):.1f}" cy="{sy(uy):.1f}" r="7" fill="{UPPER}" stroke="white" stroke-width="2"/>',
            f'<circle cx="{sx(lx):.1f}" cy="{sy(ly):.1f}" r="8" fill="{LOWER}" stroke="white" stroke-width="2"/>',
        ]
        dx, dy = label_offsets[index % len(label_offsets)]
        svg.append(
            f'<text x="{sx(lx) + dx:.1f}" y="{sy(ly) + dy:.1f}" fill="{INK}" font-family="{FONT}" font-size="14" font-weight="650">{esc(anonymous_id)}</text>'
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


def mix_color(base: str, strength: float) -> str:
    """Mix a color with white; strength is constrained to 0..1."""
    strength = max(0.0, min(1.0, strength))
    rgb = tuple(int(base[index : index + 2], 16) for index in (1, 3, 5))
    mixed = tuple(round(255 - (255 - value) * strength) for value in rgb)
    return "#" + "".join(f"{value:02x}" for value in mixed)


def format_delta(value: float, digits: int = 1) -> str:
    sign = "+" if value > 0 else ""
    if digits == 0:
        return f"{sign}{value:.0f}"
    return f"{sign}{value:.{digits}f}"


def change_matrix(
    data: pd.DataFrame,
    *,
    figure_number: str,
    title: str,
    subtitle: str,
    row_label: str,
    metric_specs: list[tuple[str, str, int]],
    width: int,
    height: int,
    note: str,
    group_column: str | None = None,
) -> str:
    """Render an individual-level delta matrix."""
    left = 110
    label_w = 150 if group_column else 110
    top = 210
    bottom_note = 80
    row_h = (height - top - bottom_note) / (len(data) + 1)
    cell_gap = 12
    table_left = left + label_w
    table_right = width - 70
    cell_w = (table_right - table_left) / len(metric_specs)
    max_abs = {
        column: max(float(data[column].abs().max()), 1e-9)
        for column, _, _ in metric_specs
    }
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{figure_number}：{esc(title)}</title>',
        f'<desc id="desc">{esc(subtitle)}</desc>',
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        f'<text x="60" y="64" fill="{INK}" font-family="{FONT}" font-size="34" font-weight="800">{figure_number}　{esc(title)}</text>',
        f'<text x="60" y="105" fill="{MUTED}" font-family="{FONT}" font-size="18">{esc(subtitle)}</text>',
        f'<rect x="{width - 405}" y="132" width="18" height="18" rx="4" fill="{mix_color(LOWER,.85)}"/><text x="{width - 378}" y="147" fill="{INK}" font-family="{FONT}" font-size="14">增加</text>',
        f'<rect x="{width - 310}" y="132" width="18" height="18" rx="4" fill="#f1eee5"/><text x="{width - 283}" y="147" fill="{INK}" font-family="{FONT}" font-size="14">持平</text>',
        f'<rect x="{width - 215}" y="132" width="18" height="18" rx="4" fill="{mix_color(UPPER,.85)}"/><text x="{width - 188}" y="147" fill="{INK}" font-family="{FONT}" font-size="14">減少</text>',
        f'<text x="{left}" y="{top - 22}" fill="{MUTED}" font-family="{FONT}" font-size="14" font-weight="700">{esc(row_label)}</text>',
    ]
    for index, (_, label, _) in enumerate(metric_specs):
        x = table_left + index * cell_w + cell_w / 2
        svg.append(
            f'<text x="{x:.1f}" y="{top - 22}" text-anchor="middle" fill="{INK}" font-family="{FONT}" font-size="15" font-weight="750">{esc(label)}</text>'
        )

    for row_index, (_, row) in enumerate(data.iterrows()):
        y = top + row_index * row_h
        if row_index % 2 == 0:
            svg.append(
                f'<rect x="55" y="{y - 4:.1f}" width="{width - 110}" height="{row_h:.1f}" rx="8" fill="#ffffff" fill-opacity=".55"/>'
            )
        anonymous_id = row["匿名代碼"]
        svg.append(
            f'<text x="{left}" y="{y + row_h / 2 + 5:.1f}" fill="{INK}" font-family="{FONT}" font-size="15" font-weight="700">{esc(anonymous_id)}</text>'
        )
        if group_column:
            group = str(row[group_column])
            short = "先備組" if group == "上學期作品名單內" else "新加入"
            color = GOLD if short == "先備組" else "#6d83b5"
            svg.append(
                f'<circle cx="{left + 62}" cy="{y + row_h / 2:.1f}" r="6" fill="{color}"/>'
            )
            svg.append(
                f'<text x="{left + 74}" y="{y + row_h / 2 + 5:.1f}" fill="{MUTED}" font-family="{FONT}" font-size="13">{short}</text>'
            )
        for col_index, (column, _, digits) in enumerate(metric_specs):
            value = float(row[column])
            strength = 0.15 + 0.78 * abs(value) / max_abs[column] if value else 0
            color = (
                mix_color(LOWER, strength)
                if value > 0
                else mix_color(UPPER, strength)
                if value < 0
                else "#f1eee5"
            )
            x = table_left + col_index * cell_w + cell_gap / 2
            svg.append(
                f'<rect x="{x:.1f}" y="{y + 5:.1f}" width="{cell_w - cell_gap:.1f}" height="{row_h - 10:.1f}" rx="9" fill="{color}"/>'
            )
            text_color = "#ffffff" if strength > 0.6 else INK
            svg.append(
                f'<text x="{x + (cell_w - cell_gap) / 2:.1f}" y="{y + row_h / 2 + 6:.1f}" text-anchor="middle" fill="{text_color}" font-family="{FONT}" font-size="15" font-weight="750">{format_delta(value, digits)}</text>'
            )

    summary_y = top + len(data) * row_h + row_h / 2
    svg.append(
        f'<text x="{left}" y="{summary_y + 5:.1f}" fill="{INK}" font-family="{FONT}" font-size="14" font-weight="800">增／平／減</text>'
    )
    for col_index, (column, _, _) in enumerate(metric_specs):
        values = data[column]
        summary = f"{int((values > 0).sum())}／{int((values == 0).sum())}／{int((values < 0).sum())}"
        x = table_left + col_index * cell_w + cell_w / 2
        svg.append(
            f'<text x="{x:.1f}" y="{summary_y + 5:.1f}" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="14" font-weight="700">{summary}</text>'
        )
    svg += [
        f'<text x="60" y="{height - 28}" fill="{MUTED}" font-family="{FONT}" font-size="14">註：{esc(note)}</text>',
        "</svg>",
    ]
    return "\n".join(svg)


def figure3(longitudinal: pd.DataFrame) -> str:
    metrics = [
        ("媒體_變化", "媒體 Δ", 0),
        ("排版_變化", "排版 Δ", 0),
        ("字數_變化", "文本字元 Δ", 0),
        ("術語密度_變化", "術語密度 Δ", 1),
        ("批判思考_變化", "反思比例 Δpp", 1),
    ]
    return change_matrix(
        longitudinal,
        figure_number="圖三",
        title="相同學生的跨學期個別變化",
        subtitle="下學期期末減上學期期末｜高信度配對 n=8",
        row_label="匿名代碼",
        metric_specs=metrics,
        width=1400,
        height=980,
        note="正值代表指標增加、負值代表減少；文本長度與術語密度的增加不必然等同品質提升。",
    )


def assignment_final_data(
    assignment: pd.DataFrame, final: pd.DataFrame
) -> pd.DataFrame:
    common = assignment.merge(
        final, on="匿名代碼", suffixes=("_作業", "_期末"), validate="one_to_one"
    )
    metrics = [
        ("媒體豐富度(1-4)", "媒體_變化"),
        ("排版架構(1-4)", "排版_變化"),
        ("總字數", "字數_變化"),
        ("專有名詞密度(次/千字)", "術語密度_變化"),
        ("批判思考佔比(%)", "批判思考_變化"),
    ]
    for source, target in metrics:
        common[target] = common[f"{source}_期末"] - common[f"{source}_作業"]
    group_order = {"上學期作品名單內": 0, "未見於上學期作品名單": 1}
    common["_group_order"] = common["組別"].map(group_order)
    return common.sort_values(["_group_order", "匿名代碼"]).drop(
        columns="_group_order"
    )


def figure4(common: pd.DataFrame) -> str:
    metrics = [
        ("媒體_變化", "媒體 Δ", 0),
        ("排版_變化", "排版 Δ", 0),
        ("字數_變化", "文本字元 Δ", 0),
        ("術語密度_變化", "術語密度 Δ", 1),
        ("批判思考_變化", "反思比例 Δpp", 1),
    ]
    return change_matrix(
        common,
        figure_number="圖四",
        title="下學期第一個網頁作業到期末的個別變化",
        subtitle="期末報告減第一個網頁作業｜共同學生 n=18",
        row_label="匿名代碼／組別",
        metric_specs=metrics,
        width=1400,
        height=1540,
        note="兩次任務範圍不同；字元數與術語密度變化反映作品型態差異，不可單獨解讀為退步。",
        group_column="組別",
    )


def figure5(common: pd.DataFrame) -> str:
    width, height = 1400, 980
    metrics = [
        ("媒體豐富度(1-4)", "媒體豐富度", "{:.2f}"),
        ("排版架構(1-4)", "排版架構", "{:.2f}"),
        ("總字數", "可見文本字元數", "{:,.0f}"),
        ("專有名詞密度(次/千字)", "術語密度", "{:.2f}"),
        ("批判思考佔比(%)", "批判思考比例（%）", "{:.2f}"),
    ]
    groups = [
        ("上學期作品名單內", "先備組", LOWER),
        ("未見於上學期作品名單", "新加入組", UPPER),
    ]
    positions = [(60, 160), (500, 160), (940, 160), (280, 520), (720, 520)]
    panel_w, panel_h = 400, 300
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">圖五：下學期兩組學生由第一個網頁作業到期末的平均軌跡</title>',
        '<desc id="desc">先備組與新加入組在媒體、排版、文本字元、術語密度和批判思考比例的平均值由第一個作業到期末的變化。</desc>',
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        f'<text x="60" y="64" fill="{INK}" font-family="{FONT}" font-size="34" font-weight="800">圖五　第一個網頁作業到期末的組別平均軌跡</text>',
        f'<text x="60" y="104" fill="{MUTED}" font-family="{FONT}" font-size="18">共同學生 n=18｜先備組 13 人；新加入組 5 人</text>',
        f'<circle cx="1080" cy="72" r="8" fill="{LOWER}"/><text x="1098" y="78" fill="{INK}" font-family="{FONT}" font-size="15">先備組</text>',
        f'<circle cx="1190" cy="72" r="8" fill="{UPPER}"/><text x="1208" y="78" fill="{INK}" font-family="{FONT}" font-size="15">新加入組</text>',
    ]
    for (metric, title, formatter), (x, y) in zip(metrics, positions):
        values: list[tuple[str, str, str, float, float]] = []
        for group_key, group_label, color in groups:
            rows = common[common["組別"] == group_key]
            start = float(rows[f"{metric}_作業"].mean())
            final = float(rows[f"{metric}_期末"].mean())
            values.append((group_key, group_label, color, start, final))
        all_values = [value for row in values for value in row[3:]]
        lo, hi = min(all_values), max(all_values)
        padding = max((hi - lo) * 0.22, 0.35 if "1-4" in metric else 1.0)
        lo -= padding
        hi += padding

        def py(value: float) -> float:
            return y + panel_h - 65 - (value - lo) / (hi - lo) * (panel_h - 120)

        x1, x2 = x + 95, x + panel_w - 75
        svg += [
            f'<rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}" rx="20" fill="#ffffff" stroke="#ded9cc"/>',
            f'<text x="{x + 24}" y="{y + 38}" fill="{INK}" font-family="{FONT}" font-size="20" font-weight="760">{esc(title)}</text>',
            f'<line x1="{x1}" y1="{y + panel_h - 52}" x2="{x2}" y2="{y + panel_h - 52}" stroke="{GRID}"/>',
            f'<text x="{x1}" y="{y + panel_h - 24}" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="14">第一個作業</text>',
            f'<text x="{x2}" y="{y + panel_h - 24}" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="14">期末</text>',
        ]
        for _, group_label, color, start, final in values:
            y1, y2 = py(start), py(final)
            svg += [
                f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}" stroke="{color}" stroke-width="4"/>',
                f'<circle cx="{x1}" cy="{y1:.1f}" r="7" fill="{color}" stroke="white" stroke-width="2"/>',
                f'<circle cx="{x2}" cy="{y2:.1f}" r="7" fill="{color}" stroke="white" stroke-width="2"/>',
                f'<text x="{x1 - 10}" y="{y1 - 10:.1f}" text-anchor="end" fill="{color}" font-family="{FONT}" font-size="13" font-weight="750">{formatter.format(start)}</text>',
                f'<text x="{x2 + 10}" y="{y2 - 10:.1f}" fill="{color}" font-family="{FONT}" font-size="13" font-weight="750">{formatter.format(final)}</text>',
            ]
    svg += [
        f'<text x="60" y="940" fill="{MUTED}" font-family="{FONT}" font-size="14">註：組別以是否出現在上學期作品名單為代理；兩階段任務要求不同，軌跡為描述性比較。</text>',
        "</svg>",
    ]
    return "\n".join(svg)


def write_figure(
    stem: str, svg: str, *, png_width: int, png_height: int
) -> None:
    (ROOT / f"{stem}.svg").write_text(svg, encoding="utf-8")
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(ROOT / f"{stem}.png"),
        output_width=png_width,
        output_height=png_height,
    )
    print(f"[saved] {stem}.svg")
    print(f"[saved] {stem}.png ({png_width}×{png_height})")


def main() -> int:
    longitudinal = pd.read_csv(DATA)
    assignment = pd.read_csv(ASSIGNMENT_DATA)
    final = pd.read_csv(FINAL_DATA)
    common = assignment_final_data(assignment, final)
    common[
        [
            "匿名代碼",
            "組別",
            "媒體_變化",
            "排版_變化",
            "字數_變化",
            "術語密度_變化",
            "批判思考_變化",
        ]
    ].to_csv(
        ROOT / "seismology_2026_hw2_to_final_changes.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_figure(
        "figure1_web_complexity_distribution",
        figure1(longitudinal),
        png_width=2800,
        png_height=1520,
    )
    write_figure(
        "figure2_text_analytics_trajectory",
        figure2(longitudinal),
        png_width=2800,
        png_height=1680,
    )
    write_figure(
        "figure3_longitudinal_individual_changes",
        figure3(longitudinal),
        png_width=2800,
        png_height=1960,
    )
    write_figure(
        "figure4_hw2_to_final_change_matrix",
        figure4(common),
        png_width=2800,
        png_height=3080,
    )
    write_figure(
        "figure5_hw2_to_final_group_trajectories",
        figure5(common),
        png_width=2800,
        png_height=1960,
    )
    print("[saved] seismology_2026_hw2_to_final_changes.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
