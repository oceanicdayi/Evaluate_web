#!/usr/bin/env python3
"""Build the standalone GitHub Pages research dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent


def records(path: str, columns: list[str]) -> list[dict]:
    frame = pd.read_csv(ROOT / path)
    available = [column for column in columns if column in frame.columns]
    frame = frame[available].where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


def safe_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )


def main() -> int:
    reports = {
        "longitudinal": (ROOT / "longitudinal_comparison_2025_2026.md").read_text(
            encoding="utf-8"
        ),
        "final_groups": (
            ROOT / "seismology_2026_prior_course_group_comparison.md"
        ).read_text(encoding="utf-8"),
        "hw2": (
            ROOT / "seismology_2026_hw2_prior_advantage_deep_dive.md"
        ).read_text(encoding="utf-8"),
        "representatives": (
            ROOT / "representative_final_reports_course_summary.md"
        ).read_text(encoding="utf-8"),
    }
    tables = {
        "geophysics": records(
            "results_geophysics_2025_final.csv",
            [
                "匿名代碼",
                "平台",
                "媒體豐富度(1-4)",
                "排版架構(1-4)",
                "總字數",
                "專有名詞密度(次/千字)",
                "批判思考佔比(%)",
                "狀態",
            ],
        ),
        "seismology": records(
            "results_seismology_2026_final_primary.csv",
            [
                "匿名代碼",
                "平台",
                "媒體豐富度(1-4)",
                "排版架構(1-4)",
                "總字數",
                "專有名詞密度(次/千字)",
                "批判思考佔比(%)",
                "狀態",
            ],
        ),
        "assignment": records(
            "seismology_2026_hw2_prior_advantage_evidence.csv",
            [
                "匿名代碼",
                "組別",
                "媒體豐富度(1-4)",
                "排版架構(1-4)",
                "總字數",
                "專有名詞出現次數",
                "主題涵蓋數",
                "內容發展指數",
                "遲交",
            ],
        ),
        "longitudinal": records(
            "longitudinal_comparison_2025_2026.csv",
            [
                "匿名代碼",
                "比較信度",
                "媒體_變化",
                "排版_變化",
                "字數_變化",
                "術語密度_變化",
                "批判思考_變化",
            ],
        ),
    }

    template = r"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="臺北市立大學地球物理與地震學學生網頁作品之縱向分析、組間比較與代表案例。">
  <meta name="theme-color" content="#092126">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='18' fill='%23071c21'/%3E%3Cpath d='M8 35h10l5-16 8 31 7-25 5 10h13' fill='none' stroke='%238bd5cb' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
  <title>從地球物理到地震學｜學生數位作品研究儀表板</title>
  <style>
    :root {
      --ink: #102a30;
      --deep: #071c21;
      --deep-2: #0c2b30;
      --paper: #f6f2e8;
      --paper-2: #ede7d9;
      --teal: #23a89d;
      --teal-light: #8bd5cb;
      --coral: #ef765f;
      --gold: #e8bd62;
      --muted: #617477;
      --line: rgba(16, 42, 48, .15);
      --shadow: 0 22px 70px rgba(6, 28, 33, .12);
      --radius: 22px;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
        "Noto Sans TC", sans-serif;
      line-height: 1.7;
    }
    a { color: #087d77; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    a:hover { color: #075f5a; }
    .skip {
      position: fixed; left: 12px; top: -80px; z-index: 100;
      padding: 10px 16px; color: white; background: var(--coral); border-radius: 8px;
    }
    .skip:focus { top: 12px; }
    .hero {
      position: relative;
      overflow: hidden;
      min-height: 620px;
      color: white;
      background:
        radial-gradient(circle at 82% 18%, rgba(35,168,157,.30), transparent 26%),
        radial-gradient(circle at 15% 75%, rgba(239,118,95,.20), transparent 30%),
        linear-gradient(135deg, var(--deep), var(--deep-2));
    }
    .hero::before, .hero::after {
      content: "";
      position: absolute;
      width: 600px; height: 600px;
      border: 1px solid rgba(139,213,203,.16);
      border-radius: 45% 55% 47% 53%;
      transform: rotate(18deg);
    }
    .hero::before { right: -180px; top: -260px; box-shadow: 0 0 0 55px rgba(139,213,203,.035), 0 0 0 110px rgba(139,213,203,.025); }
    .hero::after { left: -390px; bottom: -400px; box-shadow: 0 0 0 65px rgba(239,118,95,.035), 0 0 0 130px rgba(239,118,95,.02); }
    .hero-inner, .wrap { width: min(1180px, calc(100% - 40px)); margin: 0 auto; }
    .hero-inner { position: relative; z-index: 1; padding: 46px 0 76px; }
    .topline { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 760; letter-spacing: .04em; }
    .brand-mark {
      display: grid; place-items: center; width: 40px; height: 40px;
      border: 1px solid rgba(255,255,255,.35); border-radius: 50%;
      color: var(--gold); font-size: 20px;
    }
    .source-link { color: var(--teal-light); font-size: 14px; }
    .eyebrow { margin-top: 88px; color: var(--gold); font-weight: 750; letter-spacing: .18em; text-transform: uppercase; font-size: 13px; }
    h1 {
      max-width: 900px; margin: 16px 0 24px;
      font-size: clamp(42px, 7.3vw, 86px); line-height: 1.02; letter-spacing: -.045em;
    }
    .lead { max-width: 760px; margin: 0; color: #d8e7e5; font-size: clamp(18px, 2vw, 23px); }
    .hero-stats {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
      margin-top: 58px;
    }
    .hero-stat {
      padding: 22px; border: 1px solid rgba(255,255,255,.13);
      border-radius: 16px; background: rgba(255,255,255,.055); backdrop-filter: blur(8px);
    }
    .hero-stat strong { display: block; color: white; font-size: 30px; line-height: 1.15; }
    .hero-stat span { color: #a9c2c0; font-size: 13px; }
    .nav-shell {
      position: sticky; top: 0; z-index: 50;
      border-bottom: 1px solid var(--line);
      background: rgba(246,242,232,.92); backdrop-filter: blur(14px);
    }
    .tabs {
      display: flex; gap: 4px; width: min(1180px, calc(100% - 24px)); margin: auto;
      padding: 10px 0; overflow-x: auto; scrollbar-width: none;
    }
    .tabs::-webkit-scrollbar { display: none; }
    .tab {
      flex: none; border: 0; border-radius: 999px; padding: 10px 16px;
      color: #496366; background: transparent; cursor: pointer; font: inherit; font-weight: 650;
    }
    .tab:hover { background: rgba(35,168,157,.08); }
    .tab.active { color: white; background: var(--ink); }
    main { min-height: 70vh; }
    .panel { display: none; padding: 72px 0 100px; }
    .panel.active { display: block; animation: enter .35s ease both; }
    @keyframes enter { from { opacity: 0; transform: translateY(8px); } }
    .section-head { display: flex; justify-content: space-between; align-items: end; gap: 30px; margin-bottom: 34px; }
    .kicker { color: #148c83; font-size: 13px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    h2 { margin: 6px 0 0; font-size: clamp(30px, 5vw, 52px); line-height: 1.12; letter-spacing: -.035em; }
    .section-note { max-width: 430px; color: var(--muted); }
    .grid { display: grid; gap: 18px; }
    .grid-3 { grid-template-columns: repeat(3, 1fr); }
    .grid-2 { grid-template-columns: repeat(2, 1fr); }
    .card {
      padding: 28px; border: 1px solid var(--line); border-radius: var(--radius);
      background: rgba(255,255,255,.55); box-shadow: 0 8px 28px rgba(6,28,33,.035);
    }
    .card.dark { color: white; background: var(--ink); border-color: transparent; box-shadow: var(--shadow); }
    .card.coral { background: #f4d9cf; }
    .card.teal { background: #d7ece6; }
    .metric-label { color: var(--muted); font-size: 13px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    .dark .metric-label { color: #9fc0bd; }
    .metric-value { margin: 8px 0 4px; font-size: 42px; font-weight: 820; letter-spacing: -.04em; line-height: 1; }
    .metric-detail { color: var(--muted); font-size: 14px; }
    .dark .metric-detail { color: #bdd0ce; }
    .story {
      margin-top: 18px; padding: 34px; border-radius: var(--radius);
      color: white; background: linear-gradient(135deg, #133a3f, #0a252a);
    }
    .story blockquote { margin: 0; max-width: 900px; font-size: clamp(21px, 3vw, 31px); line-height: 1.45; font-weight: 620; }
    .story cite { display: block; margin-top: 18px; color: var(--gold); font-style: normal; font-size: 14px; }
    .compare-card { padding: 24px; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,.55); }
    .compare-card h3 { margin: 0 0 18px; font-size: 18px; }
    .figure-grid { display: grid; grid-template-columns: 1fr; gap: 26px; margin: 44px 0; }
    .figure-card { margin: 0; padding: 18px; border: 1px solid var(--line); border-radius: var(--radius); background: white; box-shadow: var(--shadow); }
    .figure-card img { display: block; width: 100%; height: auto; border-radius: 14px; }
    .figure-card figcaption { padding: 15px 8px 3px; color: var(--muted); font-size: 14px; }
    .figure-card figcaption strong { color: var(--ink); }
    .bar-row { display: grid; grid-template-columns: 74px 1fr 52px; align-items: center; gap: 10px; margin: 9px 0; font-size: 13px; }
    .track { height: 10px; background: #ddd9ce; border-radius: 99px; overflow: hidden; }
    .fill { height: 100%; border-radius: inherit; background: var(--teal); }
    .fill.alt { background: var(--coral); }
    .delta { display: inline-flex; align-items: center; gap: 6px; padding: 5px 9px; border-radius: 99px; color: #08756f; background: #d8eee9; font-size: 12px; font-weight: 750; }
    .evidence-list { margin: 0; padding: 0; list-style: none; }
    .evidence-list li { display: grid; grid-template-columns: 42px 1fr; gap: 14px; padding: 16px 0; border-bottom: 1px solid var(--line); }
    .evidence-list li:last-child { border: 0; }
    .evidence-num { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; color: white; background: var(--coral); font-weight: 800; }
    .evidence-list strong { display: block; }
    .evidence-list small { color: var(--muted); }
    .timeline { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-top: 30px; }
    .step { position: relative; min-height: 175px; padding: 20px 16px; color: white; background: var(--deep-2); border-radius: 16px; }
    .step::after { content: "→"; position: absolute; right: -11px; top: 50%; z-index: 2; color: var(--coral); font-size: 22px; }
    .step:last-child::after { display: none; }
    .step b { display: block; color: var(--gold); font-size: 12px; letter-spacing: .12em; }
    .step strong { display: block; margin: 10px 0; line-height: 1.25; }
    .step span { color: #b5cecb; font-size: 13px; }
    .case { overflow: hidden; padding: 0; }
    .case-top { padding: 30px; min-height: 190px; color: white; background: var(--deep); }
    .case:nth-child(2) .case-top { background: #8f3f34; }
    .case-top .term { color: var(--gold); font-size: 12px; letter-spacing: .13em; text-transform: uppercase; }
    .case-top h3 { margin: 10px 0 8px; font-size: 28px; }
    .case-top p { margin: 0; color: rgba(255,255,255,.76); }
    .case-body { padding: 30px; }
    .chips { display: flex; flex-wrap: wrap; gap: 7px; }
    .chip { padding: 6px 10px; border-radius: 999px; color: #23565a; background: #dcebe7; font-size: 12px; }
    .report-shell {
      padding: clamp(22px, 5vw, 58px); border: 1px solid var(--line); border-radius: var(--radius);
      background: #fffdf7; box-shadow: var(--shadow);
    }
    .prose { max-width: 930px; margin: auto; }
    .prose h1 { color: var(--ink); font-size: 44px; }
    .prose h2 { margin-top: 2.2em; font-size: 30px; }
    .prose h3 { margin-top: 1.8em; font-size: 21px; }
    .prose h4 { font-size: 17px; }
    .prose blockquote { margin: 24px 0; padding: 18px 22px; border-left: 4px solid var(--teal); background: #eaf3ef; }
    .prose table { display: block; width: 100%; overflow-x: auto; border-collapse: collapse; font-size: 14px; }
    .prose th, .prose td { padding: 10px 12px; border: 1px solid var(--line); text-align: left; }
    .prose th { background: var(--paper-2); }
    .prose code { padding: 2px 5px; border-radius: 5px; background: #e9e5da; }
    .table-tools { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
    .table-tabs { display: flex; flex-wrap: wrap; gap: 7px; }
    .table-btn { border: 1px solid var(--line); border-radius: 99px; padding: 8px 12px; background: white; cursor: pointer; }
    .table-btn.active { color: white; background: var(--teal); border-color: var(--teal); }
    .search { min-width: 240px; border: 1px solid var(--line); border-radius: 99px; padding: 10px 16px; background: white; font: inherit; }
    .data-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 16px; background: white; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 13px; white-space: nowrap; }
    .data-table th { position: sticky; top: 0; padding: 12px; text-align: left; color: white; background: var(--ink); }
    .data-table td { padding: 10px 12px; border-bottom: 1px solid var(--line); }
    .data-table tr:hover td { background: #f1eee5; }
    .downloads { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .download { display: block; padding: 18px; border: 1px solid var(--line); border-radius: 14px; color: var(--ink); background: white; text-decoration: none; }
    .download:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(6,28,33,.08); }
    .download small { display: block; color: var(--muted); }
    .caution { padding: 24px; border-left: 5px solid var(--gold); background: #f5ead0; border-radius: 4px 14px 14px 4px; }
    footer { padding: 50px 0; color: #b5ccca; background: var(--deep); }
    footer .wrap { display: flex; justify-content: space-between; gap: 30px; }
    footer a { color: var(--teal-light); }
    @media (max-width: 900px) {
      .hero-stats, .grid-3 { grid-template-columns: repeat(2, 1fr); }
      .grid-2 { grid-template-columns: 1fr; }
      .timeline { grid-template-columns: repeat(2, 1fr); }
      .step::after { display: none; }
      .downloads { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .hero-inner, .wrap { width: min(100% - 26px, 1180px); }
      .hero { min-height: 680px; }
      .topline { align-items: flex-start; flex-direction: column; }
      .eyebrow { margin-top: 58px; }
      .hero-stats, .grid-3 { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .timeline { grid-template-columns: 1fr; }
      .downloads { grid-template-columns: 1fr; }
      .report-shell { border-radius: 12px; }
      footer .wrap { flex-direction: column; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; animation: none !important; transition: none !important; }
    }
    @media print {
      .hero { min-height: auto; color: black; background: white; }
      .hero-inner { padding: 24px 0; }
      .nav-shell, .tabs, .source-link { display: none; }
      .panel { display: block !important; page-break-before: always; }
      .card, .report-shell { box-shadow: none; }
    }
  </style>
</head>
<body>
  <a class="skip" href="#content">跳至主要內容</a>
  <header class="hero">
    <div class="hero-inner">
      <div class="topline">
        <div class="brand"><span class="brand-mark">⌁</span> UTAIPEI · DIGITAL ARTIFACT STUDY</div>
        <a class="source-link" href="https://github.com/oceanicdayi/Evaluate_web">GitHub 研究資料庫 ↗</a>
      </div>
      <div class="eyebrow">Geophysics → Seismology · 2025–2026</div>
      <h1>從地底訊號<br>看見學習成長</h1>
      <p class="lead">以學生網頁作品為證據，追蹤兩學期的媒體整合、內容發展、學科語言與反思表達。</p>
      <div class="hero-stats">
        <div class="hero-stat"><strong>19</strong><span>上學期地球物理作品</span></div>
        <div class="hero-stat"><strong>18</strong><span>下學期地震學期末作品</span></div>
        <div class="hero-stat"><strong>20</strong><span>第一個網頁作業</span></div>
        <div class="hero-stat"><strong>13</strong><span>跨學期配對學生</span></div>
      </div>
    </div>
  </header>

  <nav class="nav-shell" aria-label="研究內容">
    <div class="tabs" role="tablist">
      <button class="tab active" data-panel="overview" role="tab">研究總覽</button>
      <button class="tab" data-panel="longitudinal" role="tab">跨學期成長</button>
      <button class="tab" data-panel="groups" role="tab">期末組間比較</button>
      <button class="tab" data-panel="assignment" role="tab">第一個網頁作業</button>
      <button class="tab" data-panel="cases" role="tab">優良代表作品</button>
      <button class="tab" data-panel="data" role="tab">資料與下載</button>
    </div>
  </nav>

  <main id="content">
    <section id="overview" class="panel active">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">Research overview</div><h2>三層證據，一條學習軌跡</h2></div>
          <p class="section-note">從同一學生的縱向變化、下學期組間差異，到第一個網頁作業的早期先備經驗效果。</p>
        </div>
        <div class="grid grid-3">
          <article class="card dark">
            <div class="metric-label">縱向配對 · 高信度 n=8</div>
            <div class="metric-value">+86.2%</div>
            <div class="metric-detail">下學期期末作品平均篇幅成長</div>
          </article>
          <article class="card coral">
            <div class="metric-label">媒體豐富度</div>
            <div class="metric-value">1.75 → 3.50</div>
            <div class="metric-detail">同一批學生由基礎呈現走向互動整合</div>
          </article>
          <article class="card teal">
            <div class="metric-label">早期主題高涵蓋</div>
            <div class="metric-value">71% vs 33%</div>
            <div class="metric-detail">上學期作品名單內 vs 名單外</div>
          </article>
        </div>
        <div class="story">
          <blockquote>最一致的成長不是「網頁變漂亮」而已，而是學生能把理論、資料、程式、儀器與反思組織成可公開說明的數位作品。</blockquote>
          <cite>研究整體觀察</cite>
        </div>

        <div class="section-head" style="margin-top:72px">
          <div><div class="kicker">Evaluation framework</div><h2>作品如何被閱讀</h2></div>
        </div>
        <div class="grid grid-3">
          <article class="card"><div class="metric-label">01 · Media</div><h3>媒體豐富度</h3><p>從純文字、圖文，到互動元件、動態視覺與多資源整合，採 1–4 級尺規。</p></article>
          <article class="card"><div class="metric-label">02 · Structure</div><h3>排版與架構</h3><p>檢查標題分區、導覽設計、頁面組織與動態資料串接，採 1–4 級尺規。</p></article>
          <article class="card"><div class="metric-label">03 · Text</div><h3>文本分析</h3><p>計算篇幅、學科專有名詞密度與批判思考訊號；後者為啟發式估計。</p></article>
        </div>

        <div class="section-head" style="margin-top:72px">
          <div><div class="kicker">Course design</div><h2>反覆發生的學習循環</h2></div>
        </div>
        <div class="timeline">
          <div class="step"><b>STEP 01</b><strong>概念與公式</strong><span>震波、折射、走時、震源與工程理論</span></div>
          <div class="step"><b>STEP 02</b><strong>圖解與案例</strong><span>互動走時圖、板塊、事件與建築反應</span></div>
          <div class="step"><b>STEP 03</b><strong>程式與資料</strong><span>Python、PyGMT、ObsPy、FFT／STFT</span></div>
          <div class="step"><b>STEP 04</b><strong>實作與場域</strong><span>感測器、野外佈站與工程參訪</span></div>
          <div class="step"><b>STEP 05</b><strong>AI 數位製作</strong><span>整理內容、程式起稿與公開部署</span></div>
          <div class="step"><b>STEP 06</b><strong>表達與反思</strong><span>解釋證據、檢查限制、修正理解</span></div>
        </div>
      </div>
    </section>

    <section id="longitudinal" class="panel">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">Matched longitudinal study</div><h2>同一批學生，兩學期之間</h2></div>
          <p class="section-note">13 人同名同學號配對；班級平均採 8 組高信度、可完整讀取的作品。</p>
        </div>
        <div class="grid grid-3">
          <div class="compare-card"><h3>媒體豐富度 <span class="delta">+1.75</span></h3><div class="bar-row"><span>上學期</span><div class="track"><div class="fill alt" style="width:43.75%"></div></div><b>1.75</b></div><div class="bar-row"><span>下學期</span><div class="track"><div class="fill" style="width:87.5%"></div></div><b>3.50</b></div></div>
          <div class="compare-card"><h3>平均字數 <span class="delta">+1,710</span></h3><div class="bar-row"><span>上學期</span><div class="track"><div class="fill alt" style="width:53.7%"></div></div><b>1,983</b></div><div class="bar-row"><span>下學期</span><div class="track"><div class="fill" style="width:100%"></div></div><b>3,693</b></div></div>
          <div class="compare-card"><h3>批判思考訊號 <span class="delta">+4.19 pp</span></h3><div class="bar-row"><span>上學期</span><div class="track"><div class="fill alt" style="width:61%"></div></div><b>6.54</b></div><div class="bar-row"><span>下學期</span><div class="track"><div class="fill" style="width:100%"></div></div><b>10.73</b></div></div>
        </div>
        <div class="caution" style="margin:28px 0 46px"><strong>解讀：</strong>媒體與篇幅的提升最一致；排版大致維持三級導覽分區。術語密度上升與下降各半，內容變長不等於術語更集中。</div>
        <div class="section-head" style="margin-top:62px">
          <div><div class="kicker">Key figures</div><h2>圖一與圖二</h2></div>
          <p class="section-note">以相同的 8 位高信度配對學生，呈現作品複雜度分布與文本指標的個別移動。</p>
        </div>
        <div class="figure-grid">
          <figure class="figure-card">
            <img src="figure1_web_complexity_distribution.svg" alt="圖一：媒體豐富度與排版架構在上下學期的一至四分人數分布長條圖">
            <figcaption><strong>圖一　學生網頁作品複雜度評分分布。</strong>媒體豐富度由上學期的 1–2 分為主，轉為下學期 6/8 人達 4 分；排版則兩學期皆以 3 分導覽分區為主。</figcaption>
          </figure>
          <figure class="figure-card">
            <img src="figure2_text_analytics_trajectory.svg" alt="圖二：八位學生的專有名詞密度與批判思考比例跨學期散布及移動箭頭">
            <figcaption><strong>圖二　文本分析指標的跨學期位移。</strong>每支箭頭連接同一位學生的上下學期作品；金色虛線為班級平均。因未取得先備成績，本圖不作高低成就分群。</figcaption>
          </figure>
        </div>
        <article class="report-shell"><div id="report-longitudinal" class="prose"></div></article>
      </div>
    </section>

    <section id="groups" class="panel">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">Final report groups</div><h2>下學期期末，兩組差別不大</h2></div>
          <p class="section-note">以是否出現在上學期期末作品名單作為先備課程代理：13 人 vs 5 人。</p>
        </div>
        <div class="grid grid-2">
          <article class="card">
            <div class="metric-label">結構面</div><div class="metric-value">4 / 3</div>
            <div class="metric-detail">兩組媒體／排版中位數完全相同</div>
          </article>
          <article class="card dark">
            <div class="metric-label">典型篇幅</div><div class="metric-value">4,053 vs 2,150</div>
            <div class="metric-detail">名單內組的字數中位數較高，但分布高度重疊</div>
          </article>
        </div>
        <div class="story">
          <blockquote>到了期末，先備課程經驗不再對媒體、排版或反思形成清楚分界；未具上學期作品紀錄者已能產出相近的數位成果。</blockquote>
          <cite>探索性排列比較均 p &gt; .50；不可作因果推論</cite>
        </div>
        <article class="report-shell" style="margin-top:46px"><div id="report-final-groups" class="prose"></div></article>
      </div>
    </section>

    <section id="assignment" class="panel">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">First webpage assignment</div><h2>先備經驗的早期內容優勢</h2></div>
          <p class="section-note">20 份「地震學第一章」網頁：上學期名單內 14 人、名單外 6 人。</p>
        </div>
        <div class="grid grid-3">
          <article class="card coral"><div class="metric-label">平均篇幅差</div><div class="metric-value">+1,743</div><div class="metric-detail">名單內組 5,012 字；名單外組 3,270 字</div></article>
          <article class="card teal"><div class="metric-label">主題涵蓋</div><div class="metric-value">7.86 vs 6.50</div><div class="metric-detail">11 項指定概念的平均涵蓋數</div></article>
          <article class="card dark"><div class="metric-label">內容發展指數</div><div class="metric-value">δ = .429</div><div class="metric-detail">篇幅、術語絕對數與主題涵蓋的探索性綜合</div></article>
        </div>
        <div class="grid grid-2" style="margin-top:28px">
          <article class="card">
            <h3>支持早期優勢的收斂證據</h3>
            <ol class="evidence-list">
              <li><span class="evidence-num">1</span><div><strong>內容較長</strong><small>平均 +1,743 字，中位數 +1,804 字</small></div></li>
              <li><span class="evidence-num">2</span><div><strong>專有名詞更多</strong><small>平均 +29 次，中位數 +49.5 次</small></div></li>
              <li><span class="evidence-num">3</span><div><strong>主題涵蓋更完整</strong><small>高涵蓋比例 71.4% vs 33.3%，OR=5.00</small></div></li>
            </ol>
          </article>
          <article class="card">
            <h3>為何不能說「全面顯著優於」</h3>
            <ol class="evidence-list">
              <li><span class="evidence-num">1</span><div><strong>媒體、排版中位數相同</strong><small>結構面沒有清楚分離</small></div></li>
              <li><span class="evidence-num">2</span><div><strong>遲交比例近似</strong><small>4/14 vs 2/6</small></div></li>
              <li><span class="evidence-num">3</span><div><strong>小樣本未達顯著</strong><small>最小探索性 p=.148</small></div></li>
            </ol>
          </article>
        </div>
        <article class="report-shell" style="margin-top:46px"><div id="report-hw2" class="prose"></div></article>
      </div>
    </section>

    <section id="cases" class="panel">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">Exemplary artifacts</div><h2>兩份作品，看見課程如何發生</h2></div>
          <p class="section-note">案例用來重建課程內容與教學法，不代表全班學生都完成相同深度。</p>
        </div>
        <div class="grid grid-2">
          <article class="card case">
            <div class="case-top"><div class="term">Geophysics · Upper semester</div><h3>匿名案例 G-01｜地球物理期末專題</h3><p>五項指標綜合百分等級最高：83.08</p></div>
            <div class="case-body">
              <div class="chips"><span class="chip">互動震測折射</span><span class="chip">PyGMT</span><span class="chip">非洲板塊</span><span class="chip">層析成像</span><span class="chip">火山監測</span><span class="chip">機器學習</span></div>
              <p>把物理公式轉成可調參數的走時模型，把板塊概念轉成程式地圖，再以專家講座連結研究方法與防災。</p>
              <span class="metric-detail">原始作品連結已依研究倫理移除</span>
            </div>
          </article>
          <article class="card case">
            <div class="case-top"><div class="term">Seismology · Lower semester</div><h3>匿名案例 S-01｜地震學整合平台</h3><p>八單元、13,091 字的課程全景</p></div>
            <div class="case-body">
              <div class="chips"><span class="chip">走時分析</span><span class="chip">FFT／STFT</span><span class="chip">震源機制</span><span class="chip">Raspberry Pi</span><span class="chip">野外佈站</span><span class="chip">工程補強</span></div>
              <p>從波動與射線理論，進展到訊號處理、感測器、野外地震儀、工程參訪，最後反思 AI 與專業判斷。</p>
              <span class="metric-detail">原始作品連結已依研究倫理移除</span>
            </div>
          </article>
        </div>
        <article class="report-shell" style="margin-top:46px"><div id="report-cases" class="prose"></div></article>
      </div>
    </section>

    <section id="data" class="panel">
      <div class="wrap">
        <div class="section-head">
          <div><div class="kicker">Open research data</div><h2>學生層級資料與完整報告</h2></div>
          <p class="section-note">搜尋、切換資料集，或下載 CSV／Markdown 進一步分析。</p>
        </div>
        <div class="table-tools">
          <div class="table-tabs">
            <button class="table-btn active" data-table="geophysics">地球物理期末</button>
            <button class="table-btn" data-table="seismology">地震學期末</button>
            <button class="table-btn" data-table="assignment">第一個網頁作業</button>
            <button class="table-btn" data-table="longitudinal">縱向配對</button>
          </div>
          <input id="table-search" class="search" type="search" placeholder="搜尋匿名代碼或組別" aria-label="搜尋資料表">
        </div>
        <div class="data-wrap"><table class="data-table"><thead id="data-head"></thead><tbody id="data-body"></tbody></table></div>

        <div class="section-head" style="margin-top:72px"><div><div class="kicker">Downloads</div><h2>分析成果下載</h2></div></div>
        <div class="downloads">
          <a class="download" href="representative_final_reports_course_summary.md"><strong>優良代表作品深度摘要</strong><small>Markdown · 課程內容與教學方式</small></a>
          <a class="download" href="longitudinal_comparison_2025_2026.md"><strong>跨學期縱向比較</strong><small>Markdown · 13 位配對學生</small></a>
          <a class="download" href="longitudinal_comparison_2025_2026.csv"><strong>縱向配對完整資料</strong><small>CSV</small></a>
          <a class="download" href="seismology_2026_prior_course_group_comparison.md"><strong>下學期期末組間比較</strong><small>Markdown · 13 vs 5</small></a>
          <a class="download" href="seismology_2026_hw2_prior_advantage_deep_dive.md"><strong>第一個作業深入研究</strong><small>Markdown · 14 vs 6</small></a>
          <a class="download" href="seismology_2026_hw2_prior_advantage_evidence.csv"><strong>第一個作業證據資料</strong><small>CSV · 主題涵蓋與內容指數</small></a>
          <a class="download" href="results_geophysics_2025_final.csv"><strong>地球物理期末結果</strong><small>CSV · 19 份</small></a>
          <a class="download" href="results_seismology_2026_final_primary.csv"><strong>地震學期末結果</strong><small>CSV · 18 份代表作</small></a>
          <a class="download" href="seismology_2026_hw2_results.csv"><strong>第一個網頁作業結果</strong><small>CSV · 20 份</small></a>
          <a class="download" href="figure1_web_complexity_distribution.svg"><strong>圖一：網頁複雜度分布</strong><small>SVG · 可直接用於論文排版</small></a>
          <a class="download" href="figure2_text_analytics_trajectory.svg"><strong>圖二：文本指標位移</strong><small>SVG · 配對散布圖</small></a>
          <a class="download" href="figure1_web_complexity_distribution.png"><strong>圖一 PNG</strong><small>2800×1520 · 高解析點陣圖</small></a>
          <a class="download" href="figure2_text_analytics_trajectory.png"><strong>圖二 PNG</strong><small>2800×1680 · 高解析點陣圖</small></a>
          <a class="download" href="PRIVACY.md"><strong>資料去識別化說明</strong><small>匿名化措施與 Git 歷史注意事項</small></a>
        </div>

        <div class="caution" style="margin-top:46px">
          <strong>方法與隱私限制：</strong>「修過上學期」以是否出現在上學期作品名單作代理，並非正式選課紀錄；媒體與排版為序位尺規；批判思考為關鍵詞啟發式；主題涵蓋只判定概念是否出現，不判斷正確性。學生資料已改用一次性匿名代碼，原始作品連結與文本預覽均已移除。所有結果適合描述趨勢，不應直接解讀為因果效果或學科成績。
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">
      <div><strong>Evaluate_web</strong><br><span>Digital Artifact Analysis · UTaipei Earth Science</span></div>
      <div><a href="https://github.com/oceanicdayi/Evaluate_web">原始碼與研究資料</a><br><span>Generated from reproducible Python analyses</span></div>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const REPORTS = __REPORTS__;
    const TABLES = __TABLES__;
    const reportTargets = {
      longitudinal: "report-longitudinal",
      final_groups: "report-final-groups",
      hw2: "report-hw2",
      representatives: "report-cases"
    };
    Object.entries(reportTargets).forEach(([key, id]) => {
      const el = document.getElementById(id);
      if (window.marked) el.innerHTML = marked.parse(REPORTS[key]);
      else { const pre = document.createElement("pre"); pre.textContent = REPORTS[key]; el.appendChild(pre); }
    });

    const tabs = [...document.querySelectorAll(".tab")];
    const panels = [...document.querySelectorAll(".panel")];
    function openPanel(id, updateHash = true) {
      if (!document.getElementById(id)) id = "overview";
      tabs.forEach(tab => {
        const active = tab.dataset.panel === id;
        tab.classList.toggle("active", active);
        tab.setAttribute("aria-selected", String(active));
      });
      panels.forEach(panel => panel.classList.toggle("active", panel.id === id));
      if (updateHash) history.replaceState(null, "", "#" + id);
      window.scrollTo({ top: document.querySelector(".nav-shell").offsetTop, behavior: "smooth" });
    }
    tabs.forEach(tab => tab.addEventListener("click", () => openPanel(tab.dataset.panel)));
    if (location.hash) openPanel(location.hash.slice(1), false);

    let activeTable = "geophysics";
    const head = document.getElementById("data-head");
    const body = document.getElementById("data-body");
    const search = document.getElementById("table-search");
    function formatValue(value) {
      if (value === null || value === undefined || value === "") return "—";
      if (typeof value === "number" && !Number.isInteger(value)) return value.toFixed(2);
      if (typeof value === "boolean") return value ? "是" : "否";
      return String(value);
    }
    function renderTable() {
      const rows = TABLES[activeTable] || [];
      const query = search.value.trim().toLowerCase();
      const filtered = query ? rows.filter(row => Object.values(row).some(value => String(value ?? "").toLowerCase().includes(query))) : rows;
      const columns = rows.length ? Object.keys(rows[0]) : [];
      head.innerHTML = `<tr>${columns.map(column => `<th>${column}</th>`).join("")}</tr>`;
      body.textContent = "";
      filtered.forEach(row => {
        const tr = document.createElement("tr");
        columns.forEach(column => {
          const td = document.createElement("td");
          td.textContent = formatValue(row[column]);
          tr.appendChild(td);
        });
        body.appendChild(tr);
      });
    }
    document.querySelectorAll(".table-btn").forEach(button => button.addEventListener("click", () => {
      activeTable = button.dataset.table;
      document.querySelectorAll(".table-btn").forEach(item => item.classList.toggle("active", item === button));
      renderTable();
    }));
    search.addEventListener("input", renderTable);
    renderTable();
  </script>
</body>
</html>
"""
    html = template.replace("__REPORTS__", safe_json(reports)).replace(
        "__TABLES__", safe_json(tables)
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"[saved] {ROOT / 'index.html'} ({len(html):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
