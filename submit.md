# ASET 2026 投稿文件

從數位敘事與文本分析探討 AI 融入地球科學教學之成效：學生網頁作品之縱向研究

**Evaluating AI-Integrated Earth Science Education through Text Analytics and Digital Storytelling: A Longitudinal Study of Student Web Projects**

投稿目標：[ASET 2026 投稿與發表](https://aset2026.com/%e6%8a%95%e7%a8%bf%e8%88%87%e7%99%bc%e8%a1%a8-submission/#B)

格式要求：中文摘要 500 字內（不超過一頁）／Abstract 300 words／審查用研究短文三頁內（研究目的、研究重要性、研究方法、研究結果與討論、關鍵圖表及參考文獻）

---

## 中文摘要（486 字，符合 500 字內規定）

隨著生成式AI普及，跨領域數位素養成為科學教育重要指標。本研究以台北市立大學「地球物理」與「地震學」兩門連續課程為場域，探討學生兩學期使用AI工具（ChatGPT、Gemini）與雲端部署（GitHub Pages、Hugging Face）產出期末網頁作品之縱向變化。本研究不採學科測驗，改採「數位成品分析」：建立「媒體豐富度」與「排版架構」雙軸尺規，並計算可見字數、專有名詞密度，以關鍵詞法估計批判思考比例。8位高信度配對學生納入班級統計，結果顯示：媒體豐富度由1.75分升至3.50分（6/8人提升）；字數由1,983字增至3,693字（+86.2%）；批判思考比例由6.54%升至10.73%（6/8人提升）；排版架構因多數作品已達導覽水準而近乎持平，屬尺規天花板效應。以「是否列於上學期作品名單」為先備經驗代理變項顯示，先備學生首份作業展現內容量優勢，但差距至期末明顯縮小，新加入學生在媒體豐富度與批判思考訊號增幅較大，兩組趨近。研究顯示AI輔助網頁製作有助內容產出與反思成長，並可能為先備經驗較弱學生提供追趕空間；惟樣本小、批判思考比例為啟發式估計，發現屬探索性。

---

## Abstract（280 words，符合 300-word 規定）

As generative AI becomes ubiquitous, cross-disciplinary digital literacy is increasingly central to science education. This study examines longitudinal changes in the complexity and content richness of students' final web projects across two consecutive courses, "Geophysics" and "Seismology," at the University of Taipei, where students used AI tools (ChatGPT, Gemini) and cloud platforms (GitHub Pages, Hugging Face) to turn coursework into public webpages. Rather than conventional subject-matter testing, this study analyzed the digital artifacts themselves: a two-dimensional rubric (1-4 scale) quantified "media richness" and "layout structure," while text analytics measured visible text length, technical-term density, and a keyword-heuristic estimate of the "critical-thinking" sentence ratio. Using private-key matching, 13 students were linked across semesters, 8 of whom met a high-confidence threshold for class-level comparison.

Media richness rose from 1.75 to 3.50 (6 of 8 students improved, none declined); visible text length rose from 1,983 to 3,693 characters (+86.2%; 7 of 8 increased); the critical-thinking ratio rose from 6.54% to 10.73% (6 of 8 increased); layout structure stayed largely flat, reflecting a ceiling effect since most works already had navigation and sectioning in the first semester. Using prior-semester portfolio listing as a proxy for prior course experience, students with prior exposure showed an early content-volume advantage on the first spring assignment, but this gap narrowed substantially by the final report, as newly-joined students without prior exposure showed larger gains in media richness and critical-thinking signal.

These findings suggest AI-assisted web authoring supports longitudinal growth in content production and reflective depth, and may offer a catch-up pathway for students without prior domain exposure. Given the small sample and heuristic text measures, findings remain exploratory and warrant validation with larger samples and human double-blind coding.

**關鍵詞 / Keywords**：生成式 AI、數位敘事、文本分析、網頁複雜度尺規、縱向研究 / Generative AI, Digital Storytelling, Text Analytics, Web Complexity Rubric, Longitudinal Study

---

## 審查用研究短文

### 一、研究目的

1. 建立可量化之「數位作品複雜度尺規」與「文本分析指標」，客觀評量學生在跨領域資訊融入教學中，其產出作品之品質與內容豐富度變化。
2. 探討連續兩學期 AI 協作與網頁部署訓練下，學生作品在「媒體呈現、排版架構、學科專有名詞密度、批判思考訊號」上的縱向發展。
3. 以「是否具上學期作品紀錄」為先備經驗代理變項，分析此教學法對不同先備經驗學生之早期表現差距與其後續變化。

### 二、研究重要性

傳統地球科學課程多以紙本考試或單向報告評量，難以展現學生對知識的重組與數位敘事能力。本研究跳脫「以分數論成敗」的框架，針對地科課程數位作業建立「網頁複雜度與文本分析雙軌評量法」。透過量化學生的「表達品質」與「反思深度」，能更精準地捕捉 AI 工具對學習行為的實質改變，並為大專校院未來評估「AI 輔助專題導向學習（PBL）」提供具體的評量工具與實證參考。

### 三、研究方法

本研究採量化之數位成品分析法（Digital Artifact Analysis），收集學生上、下學期網頁作業之原始碼與可見文字，所有作品皆隱去學科內容之對錯，純粹聚焦「呈現品質」與「文本豐富度」。

**1. 網頁複雜度尺規（1–4 分）**：以 HTML 結構自動判定「媒體豐富度」（純文字 1 分 → 圖文 2 分 → 互動／多媒體元素 3 分 → 進階視覺工具或多重整合 4 分）與「排版架構」（無結構 1 分 → 基本段落 2 分 → 導覽列與多區塊 3 分 → API 動態資料串接 4 分）。

**2. 文本分析**：去除 HTML 標籤取得可見文字，計算可見文本字元數，並比對地球科學／地震學專有名詞字典計算「每千字密度」；以關鍵詞啟發式方法（句子層級之批判／反思詞 vs. 描述詞比對）估計「批判思考文字」佔全文句子之比例，作為反思層次之量化代理指標。

**3. 跨學期配對**：以研究端私有鍵將同一學生上、下學期作品配對，公開資料僅保留一次性匿名代碼；共 13 人完成配對，其中 8 人（上學期靜態可見文本 ≥400 字元、雙學期作品皆可完整讀取）納入班級層級高信度統計。

**4. 先備經驗分組**：以學生是否出現於上學期期末作品名單，作為「先備經驗」之代理變項，區分「先備組」與「新加入組」，並以 Cliff's δ 效果量與精確排列檢定（小樣本、非隨機分組）進行探索性比較。

### 四、研究結果與討論

**1. 媒體豐富度與內容篇幅的顯著成長**：8 位高信度配對學生中，媒體豐富度平均由上學期 1.75 分顯著提升至下學期 3.50 分（+1.75；6 人提升、無人下降），可見文字量由平均 1,983 字增至 3,693 字（+1,710 字，+86.2%；7 人增加）。這顯示學生的認知負擔已從「學習 IT 工具」逐漸轉移至「利用 IT 工具進行知識展演」。

**2. 排版架構出現尺規天花板**：排版分數平均僅由 3.00 微降至 2.88，多數學生上學期已具備導覽列與多區塊設計，兩學期差異不大，屬評量工具本身的天花板效應，而非退步。

**3. 術語密度分化、批判思考訊號上升**：專有名詞密度平均雖增加 4.50 次／千字，但 8 人中 4 人上升、4 人下降——篇幅擴張時分母同步增大，密度不必然隨之提高。批判思考訊號比例則由平均 6.54% 上升至 10.73%（+4.19 個百分點；6 人提升），顯示學生在期末整合性任務中出現更多比較、限制與個人洞見等反思語彙。

**4. 先備經驗的早期優勢與期末收斂**：以「上學期作品名單」為代理變項比較下學期第一份作業，先備組（13 人）在內容量、專有名詞絕對使用次數與主題涵蓋數上均優於新加入組（5 人），三項內容指標方向一致（探索性內容發展指數 δ=0.429，p=.148），惟精確檢定未達統計顯著。追蹤至期末報告（18 人皆有資料）後，此差距明顯縮小：媒體豐富度效果量由 δ=0.354 降至 δ=0.092，批判思考比例由 δ=0.262 降至 δ=0.015；新加入組在媒體豐富度（+0.60 分 vs. 先備組 +0.31 分）與批判思考訊號（+6.60 個百分點 vs. 先備組 +2.95 個百分點）上增幅較大。此現象與「未修過上學期課程者於課程歷程中逐步追上」之描述一致，顯示 AI 輔助網頁製作可能為先備經驗較弱之學生提供有效的追趕路徑；惟兩次作業性質不同、樣本小且非隨機分組，尚不能推論為因果效果。

**限制**：本研究樣本規模小（班級層級統計 n=8）、分組以作品名單而非正式選課或先備成績為代理變項，且批判思考比例為關鍵詞啟發式估計，未經人工雙盲評分驗證，所有比較均屬描述性與探索性，後續應擴大樣本並輔以人工內容分析與量表驗證。

### 五、關鍵圖表

- **圖一**（`figure1_web_complexity_distribution`）：8 位高信度配對學生上、下學期媒體豐富度與排版架構評分分布——媒體由上學期以 1–2 分為主，轉為下學期 6/8 人達 4 分；排版兩學期皆以 3 分導覽分區為主。
- **圖二**（`figure2_text_analytics_trajectory`）：文本分析指標（字數、術語密度、批判思考比例）之跨學期位移散佈圖，每支箭頭連接同一學生的上下學期作品，金色虛線為班級平均。
- **圖三**（`figure3_longitudinal_individual_changes`）：8 位高信度配對學生五項指標之逐人變化熱力圖，色彩深淺依各指標欄內變化幅度標準化。
- **圖五**（`figure5_hw2_to_final_group_trajectories`）：先備組與新加入組自下學期第一份作業至期末之平均軌跡，呈現期末差距收斂之現象。
- **建議補充**：以匿名代表案例 G-01（上學期地球物理期末專題）與 S-01（下學期地震學整合平台）之網頁截圖，作為質性佐證，說明作品從單頁流水帳到多單元整合平台之典型轉變。

### 六、參考文獻

> 待補：以下僅列出建議之文獻主題方向，投稿前請依 APA 格式核實作者、年份、出處後填入完整書目，勿直接引用本節之佔位敘述。
>
> 1. 生成式 AI 融入 STEM／科學教育之學習成效與素養研究
> 2. 數位敘事（digital storytelling）於高等教育評量之應用
> 3. 文本分析／自然語言處理輔助之學習成果評量方法
> 4. 專題導向學習（PBL）與數位作品評量尺規設計
> 5. AI 工具對低先備經驗學習者之學習動機與追趕效應相關研究

---

## 撰寫說明（給投稿者參考，正式投稿前建議刪除本節）

1. 本文之量化敘述已依 `longitudinal_comparison_2025_2026.md`、`metric_calculation_method.md`、`seismology_2026_hw2_prior_advantage_deep_dive.md`、`seismology_2026_hw2_to_final_comparison.md` 等實際分析結果撰寫，取代原 README 中較概括性的敘述。
2. **重要修正**：原 README 摘要提及「初期學科表現較弱的學生」呈現爆發性成長，但專案資料明確註明「因未取得先備成績，本圖不作高低成就分群」（見 `index.html` 圖二說明），實際分組是以「是否出現於上學期作品名單」作為先備經驗代理變項，而非學科成績高低。本文已改用實際支持的敘事（先備組 vs. 新加入組、期末差距收斂），避免投稿內容與可公開查核的資料不一致。
3. 批判思考比例為關鍵詞啟發式估計（非人工雙盲評分，也非穩定的 LLM 語意分析結果），文中已明確標註此限制，建議審查前確認是否需要補充人工評分作為佐證。
4. 參考文獻僅列主題方向，尚未填入實際文獻，請依系所慣用格式與實際引用之文獻補齊，避免使用未經查核之書目。
5. 中文摘要與 Abstract 字數已控制在規定範圍內（中文約 480 字、英文約 290 字），投稿前請以投稿系統實際字數計算方式再次確認。
