#!/usr/bin/env python3
"""
數位作品縱向分析系統 (Digital Artifact Analyzer)

依據 Program 規格，對學生網頁作品量化四個維度：
1. 媒體豐富度 (Media Richness, 1–4)
2. 排版架構 (Layout Structure, 1–4)
3. 專有名詞密度 (Technical Term Density)
4. 反思層次 / 批判思考佔比 (Critical Reflection %)

用法：
  python analyze_web.py https://oceanicdayi.github.io/Utaipei_2026_summer/
  python analyze_web.py page.html --student S001 --semester Summer2026
  python analyze_web.py urls.txt --csv results.csv
  python analyze_web.py --index https://oceanicdayi.github.io/Seismology_2026_final_report_Utaipei/

若設定環境變數 GEMINI_API_KEY，會以 Gemini 評估反思層次；
否則改用關鍵詞啟發式估計（結果欄位會標示方法）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

USER_AGENT = "UTaipei-WebArtifactAnalyzer/1.0 (+research; digital-artifact-analysis)"

# ==========================================
# 1. 初始化與設定
# ==========================================

EARTH_SCIENCE_DICT = [
    # 地震／震波
    "地震", "斷層", "板塊", "震波", "地震波", "P波", "S波", "體波", "表面波",
    "洛夫波", "雷利波", "規模", "震度", "震源", "震央", "走時", "走時圖",
    "折射", "反射", "直達波", "折射波", "反射波", "視速度", "截時",
    "司乃耳", "斯乃耳", "液化", "防災",
    # 地球構造／地球物理
    "地函", "地核", "地層", "地質", "地球物理", "地震學", "重力異常",
    "磁力異常", "震源機制", "地下構造", "波速", "介質",
    # 課程／工具相關（Program 原字典）
    "Google Antigravity", "Antigravity", "CLIL", "STEM",
    # 英文對照（教材常見）
    "P-wave", "S-wave", "Love wave", "Rayleigh wave", "seismic",
    "refraction", "reflection", "epicenter", "hypocenter",
]

REFLECTION_MARKERS = [
    "反思", "反省", "發現", "或許", "是否", "比較", "差異", "優缺點",
    "優點", "缺點", "洞見", "疑問", "質疑", "挑戰", "侷限", "限制",
    "改進", "建議", "我認為", "我覺得", "讓我", "啟發", "批判",
    "為什麼", "如何才能", "反而", "不僅", "更深化", "整合",
    "reflect", "however", "limitation", "insight", "challenge",
    "compared", "whereas", "critique",
]

DESCRIBE_MARKERS = [
    "課本", "定義", "公式", "步驟", "說明", "介紹", "包含", "使用",
    "所謂", "是指", "稱為", "流程", "作業", "課程", "教材",
]


def configure_gemini() -> Any | None:
    """若有 API Key 則回傳 Gemini model，否則 None。"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key in {"YOUR_GEMINI_API_KEY", ""}:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] Gemini 初始化失敗，改用啟發式: {exc}", file=sys.stderr)
        return None


# ==========================================
# 2. 核心分析函數
# ==========================================

def resolve_huggingface_host(url: str, timeout: int = 20) -> str | None:
    """
    huggingface.co/spaces/{user}/{repo} 的 hub 頁幾乎沒有作品本文。
    透過 Spaces API 取得實際部署 host（*.hf.space / *.static.hf.space）。
    """
    m = re.match(
        r"https?://huggingface\.co/spaces/([^/\s]+)/([^/\s?#]+)",
        url,
        flags=re.I,
    )
    if not m:
        return None
    user, repo = m.group(1), m.group(2)
    api = f"https://huggingface.co/api/spaces/{user}/{repo}"
    try:
        resp = requests.get(api, timeout=timeout, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] HF API 失敗 {user}/{repo}: {exc}", file=sys.stderr)
        return None

    host = data.get("host")
    if host:
        return host.rstrip("/") + "/"

    runtime = data.get("runtime") or {}
    domains = runtime.get("domains") or []
    for item in domains:
        domain = item.get("domain") if isinstance(item, dict) else None
        if domain:
            return f"https://{domain}/"
    return None


def resolve_fetch_url(source: str) -> tuple[str, str]:
    """
    回傳 (實際抓取 URL, 解析備註)。
    Hugging Face Space hub 頁會自動改抓部署 host。
    """
    if "huggingface.co/spaces/" in source.lower():
        host = resolve_huggingface_host(source)
        if host:
            return host, f"hf_host:{host}"
        return source, "hf_hub_fallback"
    return source, "direct"


def decode_response_text(resp: requests.Response) -> str:
    """優先使用標頭 charset / UTF-8，避免中文頁被誤判編碼。"""
    content_type = resp.headers.get("Content-Type", "")
    m = re.search(r"charset=([\w-]+)", content_type, flags=re.I)
    if m:
        resp.encoding = m.group(1)
    elif not resp.encoding or resp.encoding.lower() in {"iso-8859-1", "ascii"}:
        # requests 對無 charset 常預設 ISO-8859-1；改以內容推斷
        resp.encoding = resp.apparent_encoding or "utf-8"
    # 若仍明顯亂碼且 bytes 可 UTF-8 解碼，改用 UTF-8
    text = resp.text
    if "å" in text[:2000] and "地" not in text[:2000]:
        try:
            text = resp.content.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return text


def load_html(source: str, timeout: int = 30) -> str:
    """從 URL 或本機檔案讀取 HTML。"""
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        fetch_url, note = resolve_fetch_url(source)
        if note.startswith("hf_host:"):
            print(f"[info] HF Space 改抓部署頁: {fetch_url}", file=sys.stderr)
        resp = requests.get(
            fetch_url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        return decode_response_text(resp)
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {source}")
    return path.read_text(encoding="utf-8")


def _js_object_array_to_json(js_array: str) -> list[dict[str, Any]]:
    """把簡易 JS object array（const students = [...]）轉成 Python list。"""
    js2 = re.sub(r"([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', js_array)
    js2 = re.sub(r",\s*([}\]])", r"\1", js2)
    return json.loads(js2)


def classify_work_link(url: str, label: str = "") -> tuple[bool, str]:
    """
    判斷是否為應納入尺規分析的「網頁作品」。
    回傳 (是否分析, 平台標籤)。
    """
    u = url.lower()
    label_l = label.lower()
    if any(x in u for x in [".github.io", "hf.space", "huggingface.co/spaces"]):
        if "huggingface.co/spaces" in u or "hf.space" in u:
            return True, "Hugging Face Space"
        return True, "GitHub Pages"
    if "streamlit.app" in u:
        return True, "Streamlit"
    if "gemini.google.com/share" in u:
        return True, "Gemini"
    # 明顯非作品網頁本體
    skip_hosts = (
        "github.com/",
        "github.dev/",
        "colab.research.google.com",
        "eeclass.utaipei.edu.tw",
        ".m4a",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
    )
    if any(x in u for x in skip_hosts):
        return False, label or "attachment"
    if "作品" in label or "website" in label_l or "report" in label_l:
        return True, label or "Web"
    return False, label or "other"


def parse_geophysics_students_js(html: str, semester: str) -> list[dict[str, Any]] | None:
    """解析地球物理展示頁內嵌的 const students = [...] mid。"""
    m = re.search(r"const\s+students\s*=\s*(\[\s*{.*?}\s*\])\s*;", html, flags=re.S)
    if not m:
        return None
    try:
        students = _js_object_array_to_json(m.group(1))
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] 無法解析 students JS 陣列: {exc}", file=sys.stderr)
        return None

    records: list[dict[str, Any]] = []
    for s in students:
        sid = str(s.get("studentId") or s.get("id") or "unknown").upper()
        name = s.get("name") or ""
        links = s.get("links") or []
        extras = [
            lk
            for lk in links
            if not classify_work_link(lk.get("url", ""), lk.get("label", ""))[0]
        ]
        work_links = []
        for lk in links:
            url = (lk.get("url") or "").strip()
            label = lk.get("label") or ""
            ok, platform = classify_work_link(url, label)
            if ok:
                work_links.append((url, platform, label))

        # 每位學生優先分析 GitHub Pages / Streamlit / HF；Gemini 僅在沒有其他作品時納入
        preferred = [w for w in work_links if w[1] != "Gemini"]
        chosen = preferred if preferred else work_links

        # 同網域多頁時保留主站（標籤含「作品」者優先，否則第一筆）
        if chosen:
            mains = [w for w in chosen if "作品" in w[2] or w[1] in {"Streamlit", "Hugging Face Space"}]
            if mains:
                # 仍保留所有 github.io 主站與 streamlit；略過同站 detail 子頁避免重複
                dedup: list[tuple[str, str, str]] = []
                seen_netloc_path: set[str] = set()
                ordered = mains + [w for w in chosen if w not in mains]
                for url, platform, label in ordered:
                    parsed = urlparse(url)
                    key = f"{parsed.netloc}{parsed.path}"
                    # detail.html / 週次子頁：若已有同站主頁則略過
                    if "detail.html" in parsed.path and any(
                        urlparse(u).netloc == parsed.netloc for u, _, _ in dedup
                    ):
                        continue
                    if key in seen_netloc_path:
                        continue
                    seen_netloc_path.add(key)
                    dedup.append((url, platform, label))
                chosen = dedup

        if not chosen:
            records.append(
                {
                    "student_id": sid,
                    "name": name,
                    "semester": semester,
                    "platform": "(無可分析網頁)",
                    "source": "",
                    "attachment_count": len(extras),
                    "html_content": "",
                    "error": "no_web_link",
                }
            )
            continue

        for url, platform, _label in chosen:
            records.append(
                {
                    "student_id": sid,
                    "name": name,
                    "semester": semester,
                    "platform": platform,
                    "source": url,
                    "attachment_count": len(extras),
                }
            )
    return records


def parse_final_report_index(index_url: str, timeout: int = 30) -> list[dict[str, Any]]:
    """
    解析期末報告彙整頁，抽出每位學生的網頁作品連結。

    支援：
    1. 地震學彙整頁：article.station + a.rlink
    2. 地球物理展示頁：const students = [...]（JS 內嵌資料）
    3. 後備：頁面外部 http(s) 連結
    """
    resp = requests.get(index_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    html = decode_response_text(resp)
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    # 依 URL 粗分學期標籤
    if "Geophysics" in index_url or "geophysic" in index_url.lower():
        semester = "Geophysics_2025_final"
    elif "Seismology" in index_url:
        semester = "Seismology_2026_final"
    else:
        semester = "final_report"

    # 1) 地球物理：JS students 陣列
    geo = parse_geophysics_students_js(html, semester=semester)
    if geo is not None:
        print(f"[info] 以 JS students 陣列解析，共 {len(geo)} 筆作品連結", file=sys.stderr)
        return geo

    # 2) 地震學：article.station
    articles = soup.select("article.station")
    if articles:
        for art in articles:
            sid_el = art.select_one(".code")
            name_el = art.select_one("h2")
            sid = sid_el.get_text(strip=True) if sid_el else art.get("id", "unknown")
            name = name_el.get_text(strip=True) if name_el else ""
            attach_n = len(art.select(".attach a"))
            web_links = art.select("a.rlink")
            if not web_links:
                records.append(
                    {
                        "student_id": sid,
                        "name": name,
                        "semester": semester,
                        "platform": "(無網頁連結)",
                        "source": "",
                        "attachment_count": attach_n,
                        "html_content": "",
                        "error": "no_web_link",
                    }
                )
                continue
            for a in web_links:
                platform = ""
                tag = a.select_one(".ltag")
                if tag:
                    platform = tag.get_text(strip=True)
                url = a.get("href", "").strip()
                records.append(
                    {
                        "student_id": sid,
                        "name": name,
                        "semester": semester,
                        "platform": platform,
                        "source": url,
                        "attachment_count": attach_n,
                    }
                )
        return records

    # 3) 後備：抓所有外部 http(s) 連結（排除本站 PDF/附件）
    print("[warn] 找不到已知彙整結構，改抓頁面外連。", file=sys.stderr)
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        absu = urljoin(index_url, href)
        if not absu.startswith("http"):
            continue
        if urlparse(absu).netloc == urlparse(index_url).netloc:
            continue
        ok, platform = classify_work_link(absu, a.get_text(" ", strip=True))
        if not ok:
            continue
        if absu in seen:
            continue
        seen.add(absu)
        records.append(
            {
                "student_id": f"LINK{len(records)+1:02d}",
                "name": a.get_text(" ", strip=True)[:40],
                "semester": semester,
                "platform": platform,
                "source": absu,
                "attachment_count": 0,
            }
        )
    return records


def analyze_web_complexity(html_content: str) -> tuple[int, int, dict[str, Any]]:
    """
    分析網頁複雜度，回傳「媒體豐富度」與「排版架構」分數 (1-4分)。
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # --- 評估 A: 媒體豐富度 (Media Richness) ---
    images = soup.find_all("img")
    interactive = soup.find_all(["canvas", "svg", "audio", "video", "iframe"])
    # script 文字與 src 都納入掃描（外部 chart.js 等常見於 src）
    scripts = soup.find_all("script")
    script_blob = " ".join(
        ((s.get("src") or "") + " " + (s.string or s.get_text() or "")) for s in scripts
    )
    has_advanced_scripts = bool(
        re.search(r"antigravity|three\.js|d3(\.js)?|chart\.?js|plotly|leaflet", script_blob, re.I)
    )
    # CSS/連結層面的進階視覺資源
    link_blob = " ".join((a.get("href") or "") for a in soup.find_all("link"))
    has_advanced_assets = bool(
        re.search(r"three|d3|chart|plotly|leaflet|antigravity", link_blob, re.I)
    )

    media_score = 1
    if has_advanced_scripts or has_advanced_assets or len(interactive) > 1:
        media_score = 4
    elif interactive:
        media_score = 3
    elif images:
        media_score = 2

    # --- 評估 B: 排版與架構 (Layout Structure) ---
    structure = soup.find_all(["h1", "h2", "div", "section", "article", "main"])
    nav_like = soup.find_all(["nav", "header", "footer"])
    has_api_or_dynamic = bool(
        re.search(r"\bfetch\s*\(|axios|XMLHttpRequest|\.getJSON\(|/api/|graphql", script_blob, re.I)
    )
    # 多頁跡象：內部錨點導覽或明確分頁連結
    anchors = soup.find_all("a", href=True)
    multi_page_signals = sum(
        1
        for a in anchors
        if a["href"].startswith("#")
        or a["href"].endswith(".html")
        or "page" in a["href"].lower()
    )

    layout_score = 1
    if has_api_or_dynamic:
        layout_score = 4
    elif nav_like and len(structure) > 3:
        layout_score = 3
    elif structure:
        layout_score = 2

    details = {
        "img_count": len(images),
        "interactive_count": len(interactive),
        "interactive_tags": sorted({t.name for t in interactive}),
        "structure_count": len(structure),
        "nav_header_footer": len(nav_like),
        "script_count": len(scripts),
        "has_advanced_scripts": has_advanced_scripts or has_advanced_assets,
        "has_api_or_dynamic": has_api_or_dynamic,
        "multi_page_link_signals": multi_page_signals,
    }
    return media_score, layout_score, details


def analyze_text_density(html_content: str) -> tuple[int, float, int, str, list[tuple[str, int]]]:
    """計算字數與專有名詞密度。"""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    total_length = len(text)
    if total_length == 0:
        return 0, 0.0, 0, text, []

    term_hits: list[tuple[str, int]] = []
    term_count = 0
    # 較長詞優先，避免短詞重複計入（簡化版）
    for term in sorted(set(EARTH_SCIENCE_DICT), key=len, reverse=True):
        count = text.count(term) if not re.search(r"[A-Za-z]", term) else len(
            re.findall(re.escape(term), text, flags=re.I)
        )
        if count:
            term_hits.append((term, count))
            term_count += count

    density = (term_count / total_length) * 1000
    return total_length, round(density, 2), term_count, text, term_hits


def analyze_reflection_level_heuristic(text: str) -> float:
    """無 API 時的啟發式批判思考佔比估計。"""
    if len(text) < 50:
        return 0.0
    # 以句為單位粗估
    sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", text) if s.strip()]
    if not sentences:
        return 0.0

    critical = 0
    descriptive = 0
    for sent in sentences:
        c_hits = sum(1 for m in REFLECTION_MARKERS if m.lower() in sent.lower())
        d_hits = sum(1 for m in DESCRIBE_MARKERS if m.lower() in sent.lower())
        if c_hits > d_hits and c_hits > 0:
            critical += 1
        elif d_hits > 0 or c_hits == 0:
            descriptive += 1
        else:
            critical += 1

    ratio = 100.0 * critical / max(len(sentences), 1)
    return round(min(100.0, max(0.0, ratio)), 1)


def analyze_reflection_level(text: str, model: Any | None = None) -> tuple[float, str]:
    """
    使用 Gemini（若可用）分析批判性思考文字比例；否則啟發式。
    回傳 (百分比, 方法名稱)。
    """
    if len(text) < 50:
        return 0.0, "too_short"

    if model is not None:
        prompt = f"""
你是一個教育評量專家。請分析以下學生的報告文本，區分出「描述性文字」(單純描述課本知識、實驗步驟) 與「批判性思考文字」(包含探討優缺點、提出疑問、反思、比較差異、個人洞見)。
請直接回傳一個數字（0 到 100），代表「批判性思考文字」在整篇文章中所佔的百分比。不要回傳其他文字。

學生文本：
{text[:3000]}
"""
        try:
            response = model.generate_content(prompt)
            critical_ratio = float(re.search(r"\d+(?:\.\d+)?", response.text.strip()).group())
            return round(min(100.0, max(0.0, critical_ratio)), 1), "gemini"
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] AI 分析出錯，改用啟發式: {exc}", file=sys.stderr)

    return analyze_reflection_level_heuristic(text), "heuristic"


# ==========================================
# 3. 執行分析與資料整理
# ==========================================

def analyze_record(
    student_id: str,
    semester: str,
    html_content: str,
    source: str = "",
    model: Any | None = None,
    name: str = "",
    platform: str = "",
    attachment_count: int = 0,
    error: str = "",
) -> dict[str, Any]:
    if error or not html_content:
        return {
            "學號": student_id,
            "姓名": name,
            "學期": semester,
            "平台": platform,
            "來源": source,
            "附件數": attachment_count,
            "狀態": error or "empty_html",
            "媒體豐富度(1-4)": None,
            "排版架構(1-4)": None,
            "總字數": 0,
            "專有名詞出現次數": 0,
            "專有名詞密度(次/千字)": 0.0,
            "批判思考佔比(%)": 0.0,
            "反思評量方法": "skipped",
            "img數": 0,
            "互動元件數": 0,
            "互動標籤": "",
            "進階腳本": False,
            "動態API": False,
            "命中專有名詞": "",
            "文本預覽": "",
        }

    media, layout, details = analyze_web_complexity(html_content)
    word_count, density, term_count, pure_text, term_hits = analyze_text_density(html_content)
    critical_ratio, method = analyze_reflection_level(pure_text, model=model)

    return {
        "學號": student_id,
        "姓名": name,
        "學期": semester,
        "平台": platform,
        "來源": source,
        "附件數": attachment_count,
        "狀態": "ok",
        "媒體豐富度(1-4)": media,
        "排版架構(1-4)": layout,
        "總字數": word_count,
        "專有名詞出現次數": term_count,
        "專有名詞密度(次/千字)": density,
        "批判思考佔比(%)": critical_ratio,
        "反思評量方法": method,
        "img數": details["img_count"],
        "互動元件數": details["interactive_count"],
        "互動標籤": ",".join(details["interactive_tags"]),
        "進階腳本": details["has_advanced_scripts"],
        "動態API": details["has_api_or_dynamic"],
        "命中專有名詞": "; ".join(f"{t}×{c}" for t, c in term_hits[:20]),
        "文本預覽": pure_text[:180],
    }


def process_student_data(student_records: list[dict[str, Any]], model: Any | None = None) -> pd.DataFrame:
    results = []
    for record in student_records:
        html = record.get("html_content")
        source = record.get("source") or record.get("url") or ""
        error = record.get("error", "")
        if html is None and source and not error:
            try:
                html = load_html(source)
            except Exception as exc:  # noqa: BLE001
                print(f"[error] 無法讀取 {source}: {exc}", file=sys.stderr)
                error = f"fetch_error:{exc}"
                html = ""
        if html is None and not error:
            error = "missing_html"
            html = ""
        results.append(
            analyze_record(
                student_id=record.get("student_id", "unknown"),
                semester=record.get("semester", ""),
                html_content=html or "",
                source=source,
                model=model,
                name=record.get("name", ""),
                platform=record.get("platform", ""),
                attachment_count=int(record.get("attachment_count") or 0),
                error=error,
            )
        )
    return pd.DataFrame(results)


def score_labels(media: int, layout: int) -> str:
    media_map = {1: "純文字", 2: "基礎圖文", 3: "互動多媒體", 4: "進階/動態資源"}
    layout_map = {1: "流水帳", 2: "基本段落", 3: "導覽與分區", 4: "API/動態資料"}
    return f"媒體={media_map.get(media, media)}; 排版={layout_map.get(layout, layout)}"


def print_report(df: pd.DataFrame) -> None:
    print("=== 學生作品縱向發展分析報告 ===")
    cols = [
        "學號",
        "姓名",
        "平台",
        "媒體豐富度(1-4)",
        "排版架構(1-4)",
        "總字數",
        "專有名詞密度(次/千字)",
        "批判思考佔比(%)",
        "狀態",
    ]
    show = df[[c for c in cols if c in df.columns]]
    try:
        print(show.to_markdown(index=False))
    except Exception:  # noqa: BLE001
        print(show.to_string(index=False))

    ok = df[df["狀態"] == "ok"] if "狀態" in df.columns else df
    if not ok.empty and "媒體豐富度(1-4)" in ok.columns:
        print()
        print("=== 班級摘要（僅成功抓取的網頁作品）===")
        print(f"作品數: {len(ok)}")
        print(
            "平均｜媒體={:.2f} 排版={:.2f} 字數={:.0f} 密度={:.2f} 批判%={:.1f}".format(
                ok["媒體豐富度(1-4)"].mean(),
                ok["排版架構(1-4)"].mean(),
                ok["總字數"].mean(),
                ok["專有名詞密度(次/千字)"].mean(),
                ok["批判思考佔比(%)"].mean(),
            )
        )
        print(
            "媒體分數分布:",
            ok["媒體豐富度(1-4)"].value_counts().sort_index().to_dict(),
        )
        print(
            "排版分數分布:",
            ok["排版架構(1-4)"].value_counts().sort_index().to_dict(),
        )

    print()
    for _, row in df.iterrows():
        label = f"{row.get('學號')} {row.get('姓名', '')}".strip()
        print(f"--- 詳情：{label} / {row.get('學期')} ---")
        if row.get("平台"):
            print(f"平台: {row['平台']}")
        if row.get("來源"):
            print(f"來源: {row['來源']}")
        if row.get("狀態") and row["狀態"] != "ok":
            print(f"狀態: {row['狀態']}")
            print()
            continue
        print(score_labels(int(row["媒體豐富度(1-4)"]), int(row["排版架構(1-4)"])))
        print(
            f"字數={row['總字數']} | 專有名詞={row.get('專有名詞出現次數', '?')} 次"
            f" | 密度={row['專有名詞密度(次/千字)']} /千字"
        )
        print(
            f"批判思考佔比={row['批判思考佔比(%)']}% （{row['反思評量方法']}）"
        )
        if row.get("互動標籤"):
            print(f"互動元件: {row['互動標籤']}（{row['互動元件數']}）; img={row['img數']}")
        if row.get("命中專有名詞"):
            print(f"專有名詞命中: {row['命中專有名詞']}")
        if row.get("文本預覽"):
            print(f"文本預覽: {row['文本預覽']}…")
        print()


def build_demo_records() -> list[dict[str, Any]]:
    return [
        {
            "student_id": "S001",
            "semester": "Fall (地球物理)",
            "source": "demo://fall",
            "html_content": (
                "<html><body><p>今天上地球物理，學到了重力異常。"
                "課本說重力異常跟地底下密度有關。</p></body></html>"
            ),
        },
        {
            "student_id": "S001",
            "semester": "Spring (地震學)",
            "source": "demo://spring",
            "html_content": """
            <html>
                <header><nav>首頁 | 實驗數據 | 反思</nav></header>
                <body>
                    <h1>地震波(P波與S波)分析</h1>
                    <div><canvas id="myChart"></canvas></div>
                    <script src="chart.js"></script>
                    <script> fetch('api/data') </script>
                    <p>在這次地震學實驗中，我們觀測了P波與S波的走時差異。
                    我發現，雖然課本公式是線性的，但實際疊加 Google Antigravity 模擬後，
                    邊界條件的誤差高達15%。這讓我反思，單一的理論模型是否真的能套用在複雜的斷層構造上？
                    或許結合 AI 的預測模型能彌補傳統測量工具的侷限。</p>
                </body>
            </html>
            """,
        },
    ]


def parse_sources(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.demo:
        return build_demo_records()

    if args.index:
        print(f"[info] 解析期末報告彙整頁: {args.index}", file=sys.stderr)
        records = parse_final_report_index(args.index)
        if args.semester:
            for rec in records:
                rec["semester"] = args.semester
        return records

    sources = list(args.sources)
    if len(sources) == 1 and sources[0].endswith(".txt") and Path(sources[0]).is_file():
        lines = Path(sources[0]).read_text(encoding="utf-8").splitlines()
        sources = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]

    records = []
    for idx, src in enumerate(sources, start=1):
        records.append(
            {
                "student_id": args.student or f"URL{idx:02d}",
                "semester": args.semester or "",
                "source": src,
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="數位作品縱向分析系統")
    parser.add_argument("sources", nargs="*", help="HTML 檔案、URL，或含清單的 .txt")
    parser.add_argument(
        "--index",
        default="",
        help="期末報告彙整頁 URL（自動抓每位學生的 GitHub/HF 作品連結）",
    )
    parser.add_argument("--student", default="", help="學號／作品代碼")
    parser.add_argument("--semester", default="", help="學期標籤")
    parser.add_argument("--csv", default="", help="輸出 CSV 路徑")
    parser.add_argument("--json", dest="json_path", default="", help="輸出 JSON 路徑")
    parser.add_argument("--demo", action="store_true", help="執行 Program 內建示範資料")
    args = parser.parse_args()

    if not args.sources and not args.demo and not args.index:
        parser.print_help()
        print("\n範例：")
        print("  python analyze_web.py https://oceanicdayi.github.io/Utaipei_2026_summer/")
        print(
            "  python analyze_web.py --index "
            "https://oceanicdayi.github.io/Seismology_2026_final_report_Utaipei/"
        )
        print("  python analyze_web.py --demo")
        return 2

    model = configure_gemini()
    if model is None:
        print("[info] 未設定 GEMINI_API_KEY，反思層次改用啟發式估計。", file=sys.stderr)

    records = parse_sources(args)
    # 預先載入 HTML（index 模式已含 error/no_web_link 紀錄）
    for rec in records:
        if "html_content" in rec or rec.get("error"):
            continue
        src = rec.get("source") or ""
        if not src:
            rec["error"] = "no_web_link"
            rec["html_content"] = ""
            continue
        print(f"[info] 讀取: {rec.get('student_id','')} {src}", file=sys.stderr)
        try:
            rec["html_content"] = load_html(src)
        except Exception as exc:  # noqa: BLE001
            print(f"[error] 無法讀取 {src}: {exc}", file=sys.stderr)
            rec["error"] = f"fetch_error:{exc}"
            rec["html_content"] = ""

    df = process_student_data(records, model=model)
    print_report(df)

    if args.csv:
        Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.csv, index=False, encoding="utf-8-sig")
        print(f"[saved] {args.csv}")
    if args.json_path:
        Path(args.json_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_json(args.json_path, orient="records", force_ascii=False, indent=2)
        print(f"[saved] {args.json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
