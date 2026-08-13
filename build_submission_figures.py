#!/usr/bin/env python3
"""Generate Figure 1 and Figure 2 for ASET 2026 submission.

Figure 1: Longitudinal development of matched students (n=8)
  - Left panel: Media richness (1-4) individual trajectories across semesters
  - Right panel: Critical-reflection signal (%) individual trajectories

Figure 2: Prior-experience advantage and convergence
  - Left panel: Media richness group means from HW2 to Final
  - Right panel: Critical-reflection signal group means from HW2 to Final
"""

from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent

# Try to find a CJK font
CJK_CANDIDATES = [
    "Microsoft YaHei", "Microsoft JhengHei", "SimHei", "SimSun",
    "Noto Sans CJK TC", "Noto Sans TC", "WenQuanYi Micro Hei",
    "Arial Unicode MS", "PingFang TC", "Heiti TC",
]
CJK_FONT = None
for name in CJK_CANDIDATES:
    matches = fm.findSystemFonts(fontpaths=None)
    for fp in matches:
        try:
            font = fm.FontProperties(fname=fp)
            if name.lower() in font.get_name().lower():
                CJK_FONT = font.get_name()
                break
        except Exception:
            continue
    if CJK_FONT:
        break

if CJK_FONT:
    plt.rcParams["font.family"] = CJK_FONT
    plt.rcParams["axes.unicode_minus"] = False
    print(f"[font] Using CJK font: {CJK_FONT}")
else:
    print("[font] No CJK font found; using default")

# Color palette
INK = "#123137"
PRIOR_COLOR = "#159e94"
NEW_COLOR = "#e66f5b"
GOLD = "#d7aa4b"
GRID = "#d9d5ca"
PAPER = "#fbf8ef"


def load_longitudinal() -> pd.DataFrame:
    return pd.read_csv(ROOT / "longitudinal_comparison_2025_2026_high_confidence.csv")


def load_hw2_final() -> pd.DataFrame:
    hw2 = pd.read_csv(ROOT / "seismology_2026_hw2_prior_advantage_evidence.csv")
    final = pd.read_csv(ROOT / "results_seismology_2026_final_primary.csv")
    common = hw2[["匿名代碼", "組別", "媒體豐富度(1-4)", "排版架構(1-4)", "批判思考佔比(%)"]].merge(
        final[["匿名代碼", "媒體豐富度(1-4)", "排版架構(1-4)", "批判思考佔比(%)"]],
        on="匿名代碼", suffixes=("_hw2", "_final"), validate="one_to_one"
    )
    return common


def figure1(data: pd.DataFrame) -> None:
    """Individual trajectories: media richness + CR signal across semesters."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=PAPER)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12, wspace=0.28)

    students = data["匿名代碼"].tolist()
    n = len(students)
    x = [0, 1]  # semester 1, semester 2

    # Panel A: Media richness
    ax1.set_facecolor("#ffffff")
    media_upper = data["媒體豐富度(1-4)_上學期"].values
    media_lower = data["媒體豐富度(1-4)_下學期"].values
    mean_media_upper = media_upper.mean()
    mean_media_lower = media_lower.mean()

    for i in range(n):
        ax1.plot(x, [media_upper[i], media_lower[i]],
                 color=INK, alpha=0.3, linewidth=1.2, marker="o",
                 markersize=6, markerfacecolor="white", markeredgewidth=1.5)
        ax1.annotate(students[i], (1, media_lower[i]),
                     textcoords="offset points", xytext=(8, 0),
                     fontsize=8, color=INK, alpha=0.7, va="center")

    # Mean trajectory
    ax1.plot(x, [mean_media_upper, mean_media_lower],
             color=GOLD, linewidth=4, marker="s", markersize=10,
             markerfacecolor=GOLD, markeredgecolor="white", markeredgewidth=2,
             zorder=10, linestyle="--")
    ax1.annotate(f"Mean {mean_media_upper:.2f}", (0, mean_media_upper),
                 textcoords="offset points", xytext=(-12, 10),
                 fontsize=10, color="#8a651d", fontweight="bold", ha="right")
    ax1.annotate(f"Mean {mean_media_lower:.2f}", (1, mean_media_lower),
                 textcoords="offset points", xytext=(12, 10),
                 fontsize=10, color="#8a651d", fontweight="bold")

    ax1.set_xlim(-0.3, 1.6)
    ax1.set_ylim(0.5, 4.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Geophysics\n(Semester 1)", "Seismology\n(Semester 2)"],
                        fontsize=11)
    ax1.set_yticks([1, 2, 3, 4])
    ax1.set_ylabel("Media Richness (1–4)", fontsize=12, fontweight="bold", color=INK)
    ax1.set_title("(A) Media Richness", fontsize=14, fontweight="bold", color=INK,
                  loc="left")
    ax1.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Panel B: Critical-reflection signal
    ax2.set_facecolor("#ffffff")
    cr_upper = data["批判思考佔比(%)_上學期"].values
    cr_lower = data["批判思考佔比(%)_下學期"].values
    mean_cr_upper = cr_upper.mean()
    mean_cr_lower = cr_lower.mean()

    for i in range(n):
        ax2.plot(x, [cr_upper[i], cr_lower[i]],
                 color=INK, alpha=0.3, linewidth=1.2, marker="o",
                 markersize=6, markerfacecolor="white", markeredgewidth=1.5)
        ax2.annotate(students[i], (1, cr_lower[i]),
                     textcoords="offset points", xytext=(8, 0),
                     fontsize=8, color=INK, alpha=0.7, va="center")

    # Mean trajectory
    ax2.plot(x, [mean_cr_upper, mean_cr_lower],
             color=GOLD, linewidth=4, marker="s", markersize=10,
             markerfacecolor=GOLD, markeredgecolor="white", markeredgewidth=2,
             zorder=10, linestyle="--")
    ax2.annotate(f"Mean {mean_cr_upper:.2f}%", (0, mean_cr_upper),
                 textcoords="offset points", xytext=(-12, 10),
                 fontsize=10, color="#8a651d", fontweight="bold", ha="right")
    ax2.annotate(f"Mean {mean_cr_lower:.2f}%", (1, mean_cr_lower),
                 textcoords="offset points", xytext=(12, 10),
                 fontsize=10, color="#8a651d", fontweight="bold")

    ax2.set_xlim(-0.3, 1.6)
    y_max_cr = max(cr_upper.max(), cr_lower.max()) + 5
    ax2.set_ylim(-1, y_max_cr)
    ax2.set_xticks(x)
    ax2.set_xticklabels(["Geophysics\n(Semester 1)", "Seismology\n(Semester 2)"],
                        fontsize=11)
    ax2.set_ylabel("Critical-Reflection Signal (%)", fontsize=12,
                   fontweight="bold", color=INK)
    ax2.set_title("(B) Critical-Reflection Signal", fontsize=14,
                  fontweight="bold", color=INK, loc="left")
    ax2.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=INK, alpha=0.3, linewidth=1.2, marker="o",
               markersize=6, markerfacecolor="white", markeredgewidth=1.5,
               label="Individual student"),
        Line2D([0], [0], color=GOLD, linewidth=4, marker="s", markersize=10,
               markerfacecolor=GOLD, markeredgecolor="white", markeredgewidth=2,
               linestyle="--", label="Class mean (n=8)"),
    ]
    fig.legend(handles=legend_elements, loc="upper center",
               bbox_to_anchor=(0.52, 0.96), ncol=2, fontsize=10,
               frameon=False)

    fig.suptitle("Figure 1. Longitudinal Development of Matched Students (n=8)",
                 fontsize=16, fontweight="bold", color=INK, y=0.99)
    fig.text(0.08, 0.02,
             "Note: Each line connects the same student across two semesters. "
             "CR signal is a heuristic keyword-based estimate.",
             fontsize=9, color="#617477", style="italic")

    out_png = ROOT / "figure1_longitudinal_development.png"
    out_svg = ROOT / "figure1_longitudinal_development.svg"
    fig.savefig(out_png, dpi=300, facecolor=PAPER, bbox_inches="tight")
    fig.savefig(out_svg, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_png.name}")
    print(f"[saved] {out_svg.name}")


def figure2(common: pd.DataFrame) -> None:
    """Group mean trajectories: HW2 to Final for prior vs new groups.
    Uses media richness and layout structure (matching figure5 first two panels)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=PAPER)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12, wspace=0.28)

    x = [0, 1]  # HW2, Final

    prior = common[common["組別"] == "上學期作品名單內"]
    new = common[common["組別"] == "未見於上學期作品名單"]

    # Panel A: Media richness
    ax1.set_facecolor("#ffffff")
    prior_media = [prior["媒體豐富度(1-4)_hw2"].mean(),
                   prior["媒體豐富度(1-4)_final"].mean()]
    new_media = [new["媒體豐富度(1-4)_hw2"].mean(),
                 new["媒體豐富度(1-4)_final"].mean()]

    ax1.plot(x, prior_media, color=PRIOR_COLOR, linewidth=3, marker="o",
             markersize=10, markerfacecolor=PRIOR_COLOR,
             markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax1.plot(x, new_media, color=NEW_COLOR, linewidth=3, marker="o",
             markersize=10, markerfacecolor=NEW_COLOR,
             markeredgecolor="white", markeredgewidth=2, zorder=5)

    # Annotate values
    for i, (label, val) in enumerate(zip(x, prior_media)):
        ax1.annotate(f"{val:.2f}", (i, val), textcoords="offset points",
                     xytext=(0, -18 if i == 0 else 12), fontsize=11,
                     color=PRIOR_COLOR, fontweight="bold", ha="center")
    for i, (label, val) in enumerate(zip(x, new_media)):
        ax1.annotate(f"{val:.2f}", (i, val), textcoords="offset points",
                     xytext=(0, 12 if i == 0 else -18), fontsize=11,
                     color=NEW_COLOR, fontweight="bold", ha="center")

    ax1.set_xlim(-0.3, 1.3)
    ax1.set_ylim(2.5, 4.2)
    ax1.set_xticks(x)
    ax1.set_xticklabels(["First Web\nAssignment", "Final Report"], fontsize=11)
    ax1.set_yticks([2.5, 3.0, 3.5, 4.0])
    ax1.set_ylabel("Media Richness (1–4)", fontsize=12, fontweight="bold", color=INK)
    ax1.set_title("(A) Media Richness", fontsize=14, fontweight="bold", color=INK,
                  loc="left")
    ax1.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Panel B: Layout structure
    ax2.set_facecolor("#ffffff")
    prior_layout = [prior["排版架構(1-4)_hw2"].mean(),
                    prior["排版架構(1-4)_final"].mean()]
    new_layout = [new["排版架構(1-4)_hw2"].mean(),
                  new["排版架構(1-4)_final"].mean()]

    ax2.plot(x, prior_layout, color=PRIOR_COLOR, linewidth=3, marker="o",
             markersize=10, markerfacecolor=PRIOR_COLOR,
             markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax2.plot(x, new_layout, color=NEW_COLOR, linewidth=3, marker="o",
             markersize=10, markerfacecolor=NEW_COLOR,
             markeredgecolor="white", markeredgewidth=2, zorder=5)

    # Annotate values
    for i, val in enumerate(prior_layout):
        ax2.annotate(f"{val:.2f}", (i, val), textcoords="offset points",
                     xytext=(0, -18 if i == 0 else 12), fontsize=11,
                     color=PRIOR_COLOR, fontweight="bold", ha="center")
    for i, val in enumerate(new_layout):
        ax2.annotate(f"{val:.2f}", (i, val), textcoords="offset points",
                     xytext=(0, 12 if i == 0 else -18), fontsize=11,
                     color=NEW_COLOR, fontweight="bold", ha="center")

    ax2.set_xlim(-0.3, 1.3)
    y_min_l = min(min(prior_layout), min(new_layout)) - 0.3
    y_max_l = max(max(prior_layout), max(new_layout)) + 0.3
    ax2.set_ylim(y_min_l, y_max_l)
    ax2.set_xticks(x)
    ax2.set_xticklabels(["First Web\nAssignment", "Final Report"], fontsize=11)
    ax2.set_ylabel("Layout Structure (1–4)", fontsize=12,
                   fontweight="bold", color=INK)
    ax2.set_title("(B) Layout Structure", fontsize=14,
                  fontweight="bold", color=INK, loc="left")
    ax2.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=PRIOR_COLOR, linewidth=3, marker="o",
               markersize=10, markerfacecolor=PRIOR_COLOR,
               markeredgecolor="white", markeredgewidth=2,
               label=f"Prior-experience group (n={len(prior)})"),
        Line2D([0], [0], color=NEW_COLOR, linewidth=3, marker="o",
               markersize=10, markerfacecolor=NEW_COLOR,
               markeredgecolor="white", markeredgewidth=2,
               label=f"Newly-joined group (n={len(new)})"),
    ]
    fig.legend(handles=legend_elements, loc="upper center",
               bbox_to_anchor=(0.52, 0.96), ncol=2, fontsize=10,
               frameon=False)

    fig.suptitle("Figure 2. Prior-Experience Advantage and Convergence",
                 fontsize=16, fontweight="bold", color=INK, y=0.99)
    fig.text(0.08, 0.02,
             "Note: Group means from first web assignment to final report. "
             "Tasks differ in scope; trajectories are descriptive, not pre/post tests.",
             fontsize=9, color="#617477", style="italic")

    out_png = ROOT / "figure2_prior_advantage_convergence.png"
    out_svg = ROOT / "figure2_prior_advantage_convergence.svg"
    fig.savefig(out_png, dpi=300, facecolor=PAPER, bbox_inches="tight")
    fig.savefig(out_svg, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_png.name}")
    print(f"[saved] {out_svg.name}")


def main() -> int:
    longitudinal = load_longitudinal()
    common = load_hw2_final()

    print(f"Longitudinal data: {len(longitudinal)} students")
    print(f"HW2-Final common: {len(common)} students")
    print(f"  Prior group: {len(common[common['組別']=='上學期作品名單內'])}")
    print(f"  New group: {len(common[common['組別']=='未見於上學期作品名單'])}")

    figure1(longitudinal)
    figure2(common)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())