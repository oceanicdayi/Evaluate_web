# Evaluate_web

## AI 輔助地球科學數位作品的縱向研究

**Longitudinal Development of AI-Supported Digital Artifacts in Earth Science Education**

本專案以學生在大學地球科學課程中產製的網頁作品為研究資料，探討在連續使用生成式 AI 與網頁部署工具的課程環境下，數位作品如何隨經驗累積而發展。

研究場域包括臺北市立大學「地球物理」與「地震學」課程。學生使用 ChatGPT、Gemini 等生成式 AI 工具協助整理學科內容，並透過 GitHub Pages、Hugging Face、Streamlit 等平台製作與發布數位作品。

本研究不把網頁精美程度視為學科成績，也不直接推論 AI 對學習成效的因果效果；核心是把學生作品視為 **digital artifacts**，分析其媒體整合、版面結構、內容量、學科語言與反思表達的縱向變化。

投稿目標：ASET 2026。

---

## 研究問題

### RQ1 — 縱向發展

在連續兩學期的 AI 輔助地球科學課程中，同一批學生的數位作品在媒體整合、版面結構、可見文本量、學科語言與反思訊號上如何改變？

### RQ2 — 先備數位作品經驗

已有前一學期數位作品紀錄的學生，是否在下一學期第一次網頁作業中呈現較強的內容建構表現？

### RQ3 — 組間趨同

若存在與先備經驗相關的早期差異，該差異是否在一學期共同的 AI 輔助網頁製作經驗後縮小？

完整研究問題、統計設計與可／不可支持的結論整理於：

- [`ASET_2026_research_framework.md`](ASET_2026_research_framework.md)
- [`ASET_2026_submission_draft.md`](ASET_2026_submission_draft.md)

---

## 分析架構

核心程式 `analyze_web.py` 會讀取學生網頁作品，並量化下列指標：

1. **媒體豐富度（1–4）**：由純文字、基礎圖文、互動多媒體至進階視覺／動態資源。
2. **排版架構（1–4）**：由基本內容結構、導覽與分區至 API／動態資料整合。
3. **可見文本字元數**：正規化後可見文字的字元總數。
4. **專有名詞使用**：依地球物理與地震學字典計算絕對次數與每千字密度。
5. **啟發式批判反思訊號**：依比較、限制、疑問、反思、改進等語言訊號估算批判反思句比例。

這些指標描述的是作品特徵，不直接測量地球科學內容正確性。

詳細計算方式見 [`metric_calculation_method.md`](metric_calculation_method.md)。

---

## 資料處理特色

`analyze_web.py` 已針對學生實際部署環境處理多種情況，包括：

- GitHub Pages
- Hugging Face Spaces 實際 deployment host
- Streamlit
- Gemini 分享頁登入限制
- React／SPA 稀疏 HTML
- 同站子頁補抓
- JavaScript／JSX 可見文字補充
- 中文頁面編碼處理
- 抓取限制標記

因此研究資料除了分數外，也保留「資料是否可可靠讀取」的品質資訊，避免將登入牆、SPA shell 或極短頁面誤當成完整作品。

---

## 目前主要結果

### 1. 跨學期高信度配對

完成跨學期配對 13 人，其中 8 人符合高信度比較條件。

| 指標 | 上學期平均 | 下學期平均 | 平均變化 |
| --- | ---: | ---: | ---: |
| 媒體豐富度 | 1.75 | 3.50 | +1.75 |
| 排版架構 | 3.00 | 2.88 | -0.12 |
| 可見文本字元數 | 1,983 | 3,693 | +1,710 |
| 專有名詞密度 | 21.75 | 26.24 | +4.50 次／千字 |
| 批判反思訊號 | 6.54% | 10.73% | +4.19 個百分點 |

目前最穩定的描述是：

- 媒體整合明顯增加；
- 多數高信度配對學生的作品篇幅增加；
- 多數學生的批判反思訊號增加；
- 排版大致持平，可能存在尺規天花板；
- 術語密度呈現個別分化。

完整結果見 [`longitudinal_comparison_2025_2026.md`](longitudinal_comparison_2025_2026.md)。

### 2. 第一次網頁作業的先備經驗差異

下學期第一次網頁作業中：

- 有前一學期作品紀錄：14 人
- 未見前一學期作品紀錄：6 人

先備組在可見文本量、專有名詞絕對使用次數與指定主題涵蓋上呈現方向一致的優勢。其中可見文本平均多約 1,743 字元。

然而，小樣本精確檢定未達傳統顯著水準，因此本研究將此結果稱為：

> **先備數位作品經驗與早期內容建構優勢相關的探索性證據。**

完整分析見 [`seismology_2026_hw2_prior_advantage_deep_dive.md`](seismology_2026_hw2_prior_advantage_deep_dive.md)。

### 3. 第一次作業至期末的組間趨同

同時具有第一次網頁作業與期末報告者共 18 人：

- 先備組：13 人
- 新加入組：5 人

新加入組在學期中的媒體整合與批判反思訊號增幅較大。至期末，兩組在部分作品指標上的差異較早期縮小。

這與下列描述一致：

> Prior digital-artifact experience was associated with an early advantage in content construction, whereas the between-group gap appeared to narrow over the semester as students accumulated shared experience with AI-supported web authoring.

這項結果屬於探索性觀察；第一次作業與期末報告的任務目的不同，不能視為等值前後測，也不能據此推論 AI 造成組間差距縮小。

完整結果見 [`seismology_2026_hw2_to_final_comparison.md`](seismology_2026_hw2_to_final_comparison.md)。

---

## 統計方法

目前使用：

- 描述統計（平均數、中位數）
- 個別縱向變化
- 上升／持平／下降方向計數
- Cliff's delta
- 精確秩排列檢定
- Fisher exact test

由於樣本小、非隨機分組，推論統計主要作為效果方向與分布的探索性證據，不作因果解釋。

---

## 人工評分穩定性驗證（已完成）

指導老師對 57 份作品進行兩次盲評（間隔約 30 分鐘），以檢驗媒體豐富度與排版架構尺規的評分穩定性。4 份作品因登入牆或檔案無法存取而排除，最終納入 53 份。

| 指標 | n | exact agreement | within-one | quadratic weighted κ |
| --- | ---: | ---: | ---: | ---: |
| 媒體豐富度 | 53 | 0.774 | 0.962 | 0.750 |
| 排版架構 | 53 | 0.679 | 1.000 | 0.657 |

兩項尺規均達 substantial agreement，支持尺規在同一評分者重複評分下的穩定性。人工共識與自動化評分的比較顯示，媒體 exact=0.264、排版 exact=0.509，反映自動規則式判定與人工判斷之間存在系統性差異。

批判反思訊號目前僅以關鍵詞啟發式估計，尚未經人工內容分析驗證。論文中將現有方法稱為 **rule-based operationalization**，並將批判反思比例稱為 **heuristic critical-reflection signal**。後續研究應納入獨立評分者以建立評分者間信度。

---

## 主要程式

- `analyze_web.py`：學生網頁作品核心分析
- `analyze_assignment_archive.py`：第一個網頁作業封存資料分析
- `compare_semesters.py`：跨學期期末作品縱向比較
- `compare_prior_course_groups.py`：先備作品紀錄組間比較
- `research_hw2_prior_advantage.py`：第一個作業先備優勢深入分析
- `build_figures.py`：研究圖表 SVG／PNG 產生器
- `build_dashboard.py`：GitHub Pages 研究儀表板
- `check_privacy.py`：公開資料隱私檢查

Python 套件需求見 [`requirements.txt`](requirements.txt)。

---

## 研究圖表與 Dashboard

目前研究圖表涵蓋：

1. 網頁作品複雜度分布
2. 文本指標跨學期位移
3. 個別學生縱向變化
4. 第一次作業至期末變化矩陣
5. 先備組與新加入組的平均軌跡

ASET 三頁審查短文建議只保留兩張主圖：

- **Figure 1：Longitudinal development of matched students**
- **Figure 2：Prior-experience advantage and convergence**

完整資料與其他圖表由 `build_dashboard.py` 整合至 `index.html`。

---

## 隱私與去識別化

目前公開版本採用一次性匿名代碼，並移除：

- 學生姓名與學號
- 個人作品網址
- 原始文本預覽
- 原始作業 ZIP
- 可直接識別學生的作品路徑

詳細說明見 [`PRIVACY.md`](PRIVACY.md)。

注意：較早 Git commit 曾包含直接識別資訊；若研究倫理或個資規範要求從公開 Git 歷史中完整刪除，仍需另行執行 history rewrite 與相關快取／fork 清理。

---

## 目前可以與不能支持的結論

### 可以支持

- 學生數位作品的媒體整合在連續課程中增加。
- 高信度配對學生中，多數作品的篇幅與批判反思訊號增加。
- 先備數位作品經驗與下一學期早期內容建構優勢呈方向一致的關聯。
- 新加入組在部分指標上的學期增幅較大，與組間差距逐步縮小的描述一致。

### 目前不能支持

- AI 直接造成學習成效提升。
- AI 提升地球科學知識正確性。
- AI 對「低成就學生」特別有效（目前沒有正式低成就分組變項）。
- AI 已證實能消除學習落差。
- 不同作業時間點可直接視為等值前後測。

---

## ASET 2026 投稿文件

- [`ASET_2026_research_framework.md`](ASET_2026_research_framework.md)：正式研究問題、統計框架、結論界線
- [`ASET_2026_submission_draft.md`](ASET_2026_submission_draft.md)：中文摘要、英文摘要與三頁審查短文草稿

目前論文核心訊息為：

> **This exploratory longitudinal study suggests that prior digital-artifact experience is associated with an early advantage in scientific content construction, while shared experience with AI-supported web authoring is accompanied by increasingly similar digital-artifact profiles across students over the semester.**
