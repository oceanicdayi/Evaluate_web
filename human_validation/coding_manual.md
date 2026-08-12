# Human Coding Manual

版本：v1.0（正式評分前應先以 3–5 份 calibration 作品修訂）

## 一、共同原則

1. 評分對象是「作品本身呈現的特徵」，不是學生能力、努力程度或學科正確性。
2. 不因使用特定工具名稱（例如 Chart.js、React、API）就自動給高分；人工評分看的是實際呈現與功能。
3. 正式評分時不要參考 Python 分數，也不要討論彼此分數。
4. 如遇邊界案例，先依本 manual 最接近的層級評分，並在 note 記錄原因。
5. 所有 disagreement 在 reliability 計算後才討論。

---

# A. Media Richness（1–4）

## Score 1 — Text-dominant / minimal media

作品主要由文字構成，沒有具教學意義的圖片、多媒體或互動元素。

可包含：
- 標題與段落
- 基本 CSS 裝飾
- icon 或純裝飾背景

不因裝飾性圖片而升級。

## Score 2 — Static visual integration

作品至少使用一種與內容相關的靜態視覺素材，協助理解或組織科學內容。

例如：
- 地震波示意圖
- 地圖截圖
- 實驗照片
- 靜態圖表
- infographic

重點：視覺素材具有內容功能，而非只有裝飾。

## Score 3 — Interactive or time-based media

作品至少具有一種可操作、動態或時間性媒體，且該元素與內容呈現有關。

例如：
- interactive chart
- quiz
- slider
- map interaction
- canvas visualization
- embedded video / audio
- animation that communicates scientific content

單純使用某個 JavaScript library 不足以判 3；需確認頁面實際呈現互動或動態功能。

## Score 4 — Integrated advanced media system

作品整合多種媒體／互動方式，或單一進階媒體系統被深度使用，形成明顯高於單一互動元件的資訊展示。

例如：
- 多個互動圖表 + 動畫 + 影片
- 地圖與資料視覺化聯動
- 模擬器搭配即時參數控制與解釋
- 多重 AI 生成媒體在同一作品中有目的地整合

### Media 邊界規則

- 一張 Chart.js 圖：通常 3，不自動是 4。
- 多張靜態圖片：仍可能是 2。
- 大量 CSS 動畫但與內容無關：不應因此升級。
- 單一 YouTube iframe：若只是影片嵌入，通常 3；若與其他媒體整合且形成整體學習設計才考慮 4。

---

# B. Layout Structure（1–4）

## Score 1 — Linear / weak hierarchy

內容大致依序向下堆疊，缺乏明確資訊階層或區塊組織。

例如：
- 長篇連續文字
- 很少標題
- 無明顯 section

## Score 2 — Sectioned

作品具有清楚內容區隔與基本資訊層級。

例如：
- h1 / h2
- cards
- section / article
- 章節化內容

但使用者主要仍以單一路徑閱讀。

## Score 3 — Navigable information architecture

作品具有清楚導覽結構，使用者可在不同內容區域間選擇或切換。

例如：
- navbar
- tabs
- sidebar
- multi-page structure
- section navigation

重點是資訊架構，而不是 HTML 是否出現 `<nav>`。

## Score 4 — Dynamic / data-integrated architecture

作品的資訊架構或呈現內容會依使用者操作或外部資料動態改變，形成真正的資料／互動式應用。

例如：
- API-driven content
- dynamic filtering/query
- live data dashboard
- parameter-controlled simulation
- user input changes displayed information substantially

### Layout 邊界規則

- 有 `<nav>` 但只有一個有效入口：不一定是 3。
- 有 `fetch()` 但實際頁面沒有形成動態內容：不應給 4。
- 多張 cards 但沒有可選導覽：通常 2。
- tabs / sidebar 有清楚內容切換：通常 3。

---

# C. Sentence Coding

每一句只能先選一個主要 code：`D`、`CR`、`O`。

## D — Descriptive

主要功能是陳述、解釋、重述或報告資訊。

包括：
- 科學知識定義
- 事實敘述
- 實驗步驟
- 結果描述
- 工具使用說明

例：
> P 波的傳播速度通常快於 S 波。

例：
> 本實驗先量測震源到各測站的走時。

## CR — Critical / Reflective

句子包含至少一種分析性或反思性行為：

- 比較與辨別差異
- 解釋原因或機制
- 評估優缺點
- 指出限制、不確定性或誤差來源
- 提出合理疑問
- 反思原先理解
- 提出改進方式
- 將結果連結到更廣的科學意義

例：
> 雖然理論上速度應隨介質改變，但本次結果沒有清楚呈現此趨勢，可能與初至時間判讀誤差有關。

例：
> 我原本以為加入更多資料一定能改善結果，但實際比較後發現資料品質比資料量更重要。

注意：單純出現「我認為」「我覺得」不等於 CR。

例如：
> 我認為 P 波比 S 波快。

若沒有理由、比較、評估或反思，仍判 D。

## O — Other / non-analytic

不屬於研究所關心的科學描述或反思內容。

例如：
- 導覽文字
- 按鈕說明
- 致謝
- 參考文獻片段
- 無完整語意的 fragment
- 純 UI 指令

例：
> 點擊下方按鈕查看更多內容。

---

# D. Critical-reflection ratio

人工驗證時建議主要分析：

- `CR` vs `non-CR`（D + O）以便與現行 heuristic 比較。

若之後要報更具內容意義的人工比例，可另外計算：

`CR / (CR + D)`

這會排除 UI、導覽與其他非分析句。

---

# E. Calibration procedure

正式評分前：

1. 共同選 3–5 份練習作品。
2. 兩人先各自評分，再逐項討論。
3. 把真正產生歧義的案例寫回本 manual。
4. 凍結 final manual。
5. 正式樣本重新亂序後，兩位評分者獨立評分。
6. 正式評分期間不得協商分數。

Calibration 樣本若曾被共同討論，建議不要直接納入正式 inter-rater reliability；若因樣本太小必須納入，至少需在方法中揭露。
