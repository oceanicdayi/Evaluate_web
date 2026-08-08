# Evaluate_web

從數位敘事與文本分析探討 AI 融入地球科學教學之成效：學生網頁作品之縱向研究

**Evaluating AI-Integrated Earth Science Education through Text Analytics and Digital Storytelling: A Longitudinal Study of Student Web Projects**

投稿目標：[ASET 2026 投稿與發表](https://aset2026.com/%e6%8a%95%e7%a8%bf%e8%88%87%e7%99%bc%e8%a1%a8-submission/#B)

- 中文摘要：500 字內，不超過一頁
- Abstracts：300 words
- 審查用研究短文：三頁內；需包含研究目的、研究重要性、研究方法、研究結果與討論、關鍵圖表及參考文獻

> **投稿用完整版本請見 [`submit.md`](submit.md)**（含審查用研究短文、關鍵圖表清單、參考文獻待補清單）。
> 下方摘要已依實際分析結果（`longitudinal_comparison_2025_2026.md` 等）校正，取代先前未經資料驗證的草稿版本；
> 詳見 `metric_calculation_method.md` 中「媒體豐富度尺規修正說明」。

---

## 中文摘要

隨著生成式AI普及，跨領域數位素養成為科學教育重要指標。本研究以台北市立大學「地球物理」與「地震學」兩門連續課程為場域，探討學生兩學期使用AI工具（ChatGPT、Gemini）與雲端部署（GitHub Pages、Hugging Face）產出期末網頁作品之縱向變化。本研究不採學科測驗，改採「數位成品分析」：建立「媒體豐富度」與「排版架構」雙軸尺規，並計算可見字數、專有名詞密度，以關鍵詞法估計批判思考比例。8位高信度配對學生納入班級統計，結果顯示：媒體豐富度由1.75分升至3.25分（6/8人提升）；字數由1,983字增至3,693字（+86.2%）；批判思考比例由6.54%升至10.73%（6/8人提升）；排版架構因多數作品已達導覽水準而近乎持平，屬尺規天花板效應。以「是否列於上學期作品名單」為先備經驗代理變項顯示，先備學生首份作業展現內容量優勢；追蹤至期末，字數與批判思考的組間差距縮小，但媒體豐富度差距反而擴大，顯示先備經驗優勢不會單純隨課程全面消失。研究顯示AI輔助網頁製作有助內容產出與反思成長；惟樣本小、批判思考比例為啟發式估計，發現屬探索性。

---

## Abstract

As generative AI becomes ubiquitous, cross-disciplinary digital literacy is increasingly central to science education. This longitudinal study examines changes in the complexity and content richness of students' final web projects across two consecutive courses, "Geophysics" and "Seismology," at the University of Taipei, where students used AI tools (ChatGPT, Gemini) and cloud platforms (GitHub Pages, Hugging Face) to turn coursework into public webpages.

Rather than conventional subject-matter testing, this study analyzed the digital artifacts themselves: a two-dimensional rubric (1-4 scale) quantified "media richness" and "layout structure," while text analytics measured visible text length, technical-term density, and a keyword-heuristic estimate of the "critical-thinking" sentence ratio. Among 8 high-confidence matched students, media richness rose from 1.75 to 3.25 (6 of 8 improved, none declined); visible text length rose from 1,983 to 3,693 characters (+86.2%); the critical-thinking ratio rose from 6.54% to 10.73%; layout structure stayed largely flat (a ceiling effect).

Using prior-semester portfolio listing as a proxy for prior course experience, students with prior exposure showed an early content-volume advantage. By the final report, the word-count and critical-thinking gaps between groups narrowed, but the media-richness gap widened instead — the prior-exposure group kept gaining while the newly-joined group's average score declined. This suggests AI-assisted web authoring supports longitudinal growth in content production and reflective depth, but prior experience does not simply wash out over the semester. Findings are exploratory, based on a small sample and heuristic text measures.

---

## 審查用研究短文

### 一、研究目的

1. 建立具體可量化之「數位作品複雜度尺規」與「文本分析指標」，以客觀評量學生在跨領域資訊融入教學中，其產出作品之品質與內容豐富度變化。
2. 探討在連續兩學期的 AI 協作與網頁部署訓練下，學生作品在「媒體呈現、排版架構、學科專有名詞密度、以及反思層次」上的縱向發展。
3. 分析此教學法對不同先備學術表現（尤其是初期成績較不理想）學生之學習動機與參與度的實質影響。

### 二、研究重要性

傳統地球科學課程多以紙本考試或單向報告評量，難以展現學生對知識的重組與數位敘事能力。本研究跳脫「以分數論成敗」的框架，首創針對地科課程數位作業的「網頁複雜度與文本分析雙軌評量法」。透過量化學生的「表達品質」與「反思深度」，不僅能更精準地捕捉 AI 工具對學習行為的實質改變，更為大專校院未來評估「AI 輔助專題導向學習（PBL）」提供了具體的評量工具與實證參考。

### 三、研究方法

本研究採量化之數位成品分析法（Digital Artifact Analysis），收集學生上下學期之網頁作業原始碼與文本。所有作品皆隱去地科知識之對錯，純粹聚焦於「呈現品質」與「文本豐富度」進行量化評估。

#### 1. 網頁資訊作品複雜度尺規（Rubric, 1–4 分）

兩位評分者依據以下標準進行雙盲評分：

| 評分維度 | 1 分（基礎） | 2 分（進階） | 3 分（優良） | 4 分（卓越） |
| --- | --- | --- | --- | --- |
| 媒體豐富度 | 僅有純文字 | 具備基礎圖文搭配 | 包含互動式圖表或動態網頁元素 | 深度整合多種 AI 生成資源（如語音、影片、複雜視覺架構） |
| 排版與架構 | 單頁流水帳式呈現 | 具備基本段落與標題區隔 | 具備明確的導覽列（Navbar）與多重分頁設計 | 運用 API（如 Google Antigravity）達成高度動態特效與資料串接 |

#### 2. 文本分析（Text Analytics）

- **基礎量化**：導出網頁純文字，計算總字數，並比對地球科學／地震學字典，計算「專有名詞密度（Technical Term Density）」。
- **反思層次分析（AI 輔助評量）**：運用大語言模型（如 Gemini Pro）對學生的文本進行語意分析，將語句標籤化為「描述性文字（敘述課本或實驗步驟）」與「批判性思考文字（探討優缺點、比較差異、提出疑問）」，計算後者所佔之比例。

### 四、研究結果與討論

#### 1. 作品精緻度與內容篇幅的顯著成長

8 位高信度配對學生中，媒體豐富度平均由上學期 1.75 分顯著提升至下學期 3.25 分（6 人提升、無人下降），可見文字量由平均 1,983 字增至 3,693 字（+86.2%；7 人增加）。排版架構則因多數學生上學期已具備導覽列與多區塊設計，兩學期差異不大（3.00→2.88），屬評量尺規本身的天花板效應。

#### 2. 文本數據揭示的深度學習

文本分析結果顯示，批判思考訊號比例由平均 6.54% 上升至 10.73%（+4.19 個百分點；6 人提升）；專有名詞密度則呈現分化（8 人中 4 升 4 降），顯示篇幅擴張時分母同步增大，密度不必然隨之提高。整體而言，學生並非僅是將課本內容複製貼上，而是透過 AI 輔助彙整後，釋放了更多認知空間進行高階反思。

#### 3. 先備經驗的早期優勢：期末呈現指標分歧，而非全面收斂

以「上學期作品名單」為先備經驗代理變項比較下學期第一份作業，先備組（13 人）在內容量、專有名詞絕對使用次數與主題涵蓋數上均優於新加入組（5 人）。追蹤至期末報告後，字數與批判思考比例的組間差距縮小，與「未修過上學期課程者逐步追上」的描述一致；但**媒體豐富度效果量反而由 δ=0.077 升至 δ=0.462**（先備組媒體平均由 2.92 分升至 3.38 分，新加入組則由 2.80 分降至 2.60 分），顯示先備經驗在「媒體整合」面向的優勢並未隨課程進行而消失。本研究未取得學生先備學科成績，因此無法、也不宜以「高／低成就」分群；上述分組僅以上學期作品名單作為先備經驗代理變項，且樣本小、非隨機分組，僅能視為探索性趨勢。

### 五、關鍵圖表

- **圖一**（`figure1_web_complexity_distribution`）：8 位高信度配對學生上、下學期媒體豐富度與排版架構評分分布——媒體由上學期以 1–2 分為主，轉為下學期 5/8 人達 4 分；排版兩學期皆以 3 分導覽分區為主。
- **圖二**（`figure2_text_analytics_trajectory`）：文本分析指標（字數、術語密度、批判思考比例）之跨學期位移散佈圖；因未取得先備成績，不作高／低成就分群。
- **圖五**（`figure5_hw2_to_final_group_trajectories`）：先備組與新加入組自下學期第一份作業至期末之平均軌跡——字數與批判思考比例差距收斂，媒體豐富度則反向擴大。
- **建議補充**：以匿名代表案例 G-01（上學期地球物理期末專題）與 S-01（下學期地震學整合平台）之網頁截圖，作為質性佐證。

### 六、參考文獻

（待補：請依投稿格式補上相關文獻，勿使用未經查核之書目）
