# ASET 2026 投稿草稿

## 題目

**AI 輔助地球科學數位作品的縱向發展：先備數位經驗、早期優勢與組間趨同**

**Longitudinal Development of AI-Supported Digital Artifacts in Earth Science Education: Prior Experience, Early Advantage, and Convergence**

---

## 中文摘要（投稿版草稿）

本研究探討學生在連續地球科學課程中使用生成式 AI 與網頁部署工具後，數位作品如何隨經驗累積而發展，並分析先備數位作品經驗與後續表現的關聯。研究以臺北市立大學地球物理與地震學課程之學生網頁作品為分析單位，建立規則式數位作品分析流程，量化媒體豐富度、排版架構、可見文本字元數、地球科學專有名詞使用，以及啟發式批判反思訊號。跨學期高信度配對顯示，學生作品的媒體豐富度由平均 1.75 提升至 3.50，可見文本由 1,983 增至 3,693 字元，且 8 人中有 6 人的批判反思訊號增加。進一步比較下學期第一次網頁作業發現，具有前一學期作品紀錄者在內容量、專有名詞絕對次數與指定主題涵蓋上呈現方向一致的早期優勢，但小樣本精確檢定未達顯著。至期末，新加入學生在媒體整合與反思訊號上的增幅較大，組間差距呈縮小趨勢。結果顯示，先備數位作品經驗可能與早期內容建構優勢相關，而共同的 AI 輔助網頁製作經驗則伴隨不同經驗學生之作品型態逐步趨近。由於樣本小、非隨機分組且不同時間點任務並非等值前後測，本研究結果應視為探索性證據。

**關鍵詞：** 生成式 AI、地球科學教育、數位作品、縱向研究、數位敘事

---

## Abstract

This exploratory longitudinal study examined how students' digital artifacts developed across consecutive university Earth science courses using generative AI and web-deployment tools, and whether prior digital-artifact experience was associated with later performance. Student web projects from Geophysics and Seismology courses at the University of Taipei were analyzed using a rule-based digital-artifact framework. The measures included media richness, layout structure, visible-text character count, technical-term use, and a heuristic critical-reflection signal.

Among eight high-confidence students matched across semesters, mean media richness increased from 1.75 to 3.50, while visible-text character count increased from 1,983 to 3,693. Six of the eight students also showed higher critical-reflection signals in the later semester. In the first web assignment of the Seismology course, students with records of prior-semester digital artifacts produced longer texts, used more technical terms in absolute counts, and covered more assigned disciplinary topics. These differences were directionally consistent but did not reach conventional statistical significance in exact small-sample tests. By the end of the semester, students without prior artifact records showed larger gains in media richness and critical-reflection signals, and several between-group differences became smaller.

The findings suggest that prior digital-artifact experience may be associated with an early advantage in scientific content construction, whereas shared experience with AI-supported web authoring is accompanied by increasingly similar digital-artifact profiles over time. Because the groups were not randomized, prior-course status was a proxy measure, tasks differed across time points, and the sample was small, the results should be interpreted as exploratory rather than causal.

**Keywords:** generative AI; Earth science education; digital artifacts; longitudinal analysis; digital storytelling

---

# 審查用研究短文（三頁版內容草稿）

## 一、研究目的與重要性

生成式 AI 已快速進入大學教學，但其教育效果不應只以「是否使用 AI」或單次測驗成績判斷。當學生利用 ChatGPT、Gemini 等工具協助整理科學內容，再以 GitHub Pages、Hugging Face 或其他網頁平台將學習成果轉化為可瀏覽、可互動的數位作品時，學生同時進行學科內容重組、數位敘事與資訊工具整合。這類數位成品保留了學習過程留下的結構性痕跡，因此可作為觀察學生如何使用 AI 進行知識表達的另一種證據來源。

本研究以連續兩學期的「地球物理」與「地震學」課程為場域，學生在課程中持續使用生成式 AI 與網頁部署工具製作學習成果。研究不直接把網頁精美程度視為學科成績，而是將作品視為 digital artifacts，分析其呈現形式、內容量、學科語言及反思訊號的變化。

本研究提出三個研究問題：

1. **RQ1：** 同一批學生的數位作品，在連續兩學期中如何改變？
2. **RQ2：** 已有前一學期數位作品紀錄的學生，是否在下一學期第一次網頁作業中呈現較強的內容建構表現？
3. **RQ3：** 若存在早期差異，該差異是否在一學期共同的 AI 輔助網頁製作經驗後縮小？

此研究的重要性在於：相較於只比較期末成績，本研究嘗試建立一套可重複執行的 digital-artifact analysis 方法，將學生作品本身轉化為可分析的教育研究資料，同時保留對小樣本、非隨機設計與自動評量限制的謹慎解讀。

---

## 二、研究方法

### 1. 研究資料與分析設計

研究資料來自兩個連續的大學地球科學課程。公開研究資料均以一次性匿名代碼呈現，學生姓名、學號、作品網址與原始作業內容不納入公開資料集。

分析分成三個層次：

- **跨學期縱向配對：** 完成跨學期配對 13 人，其中 8 人之兩學期作品均可完整讀取且符合高信度條件，用於 RQ1。
- **下學期第一次網頁作業組間比較：** 有前一學期作品紀錄 14 人，未見前一學期作品紀錄 6 人，用於 RQ2。
- **第一次作業至期末變化：** 同時具有第一次作業與期末報告者 18 人，其中先備組 13 人、新加入組 5 人，用於 RQ3。

「有前一學期作品紀錄」僅作為先備數位作品經驗的代理變項，不等同正式修課紀錄或學業高低成就。

### 2. 數位作品指標

研究以 Python 與 BeautifulSoup 解析 HTML，並針對動態網頁補充同站子頁與可擷取的 JavaScript／JSX 可見文字。主要指標如下：

- **媒體豐富度（1–4）：** 由純文字、基礎圖文、互動多媒體至進階視覺／動態資源。
- **排版架構（1–4）：** 由缺乏結構、基本段落、導覽與分區至 API／動態資料整合。
- **可見文本字元數：** 正規化後可見文字的字元總數。
- **專有名詞使用：** 依地球物理與地震學字典計算絕對出現次數與每千字密度。
- **啟發式批判反思訊號：** 依句子中的比較、限制、疑問、反思及改進等語言訊號，估算批判反思句所占比例。

上述指標描述的是作品特徵，不直接衡量地球科學內容正確性。其中媒體與排版為規則式操作化尺規；批判反思訊號亦非經驗證的心理量表。

### 3. 統計分析

跨學期結果以個別配對軌跡、平均值及上升／持平／下降方向呈現。先備組與新加入組的探索性比較則使用平均數、中位數、Cliff's delta 與精確秩排列檢定；指定主題高涵蓋比例使用 Fisher exact test。由於樣本小且非隨機分組，統計檢定主要用於描述分布與效果方向，而非建立因果結論。

---

## 三、研究結果

### 1. 連續課程中的數位作品發展

在 8 位高信度跨學期配對學生中，媒體豐富度由上學期平均 **1.75** 提升至下學期 **3.50**，其中 6 人提升、2 人持平、無人下降。排版架構則由 3.00 至 2.88，整體大致持平，顯示多數學生在上學期已建立導覽與分區結構，可能存在尺規天花板。

可見文本字元數由平均 **1,983** 增至 **3,693**，平均增加 1,710 字元；8 人中有 7 人增加。批判反思訊號由 6.54% 增至 10.73%，6 人增加、2 人下降。專有名詞密度則有 4 人增加、4 人下降，顯示篇幅增加並不必然伴隨更高的術語集中度。

**[Figure 1 建議：高信度配對學生之媒體豐富度與批判反思訊號跨學期個別軌跡]**

### 2. 先備數位作品經驗的早期優勢

在下學期第一次網頁作業中，先備組（n=14）的平均可見文本比新加入組（n=6）多約 **1,743 字元**。先備組亦呈現較多專有名詞絕對使用次數與較高的指定主題涵蓋數。以高涵蓋作品（至少涵蓋 8/11 個指定主題）比較，先備組為 10/14，新加入組為 2/6。

多項內容指標的效果方向一致偏向先備組，但 Cliff's delta 多屬小至中等幅度，且精確小樣本檢定未達 p < .05。因此，本研究將此結果解讀為「先備數位作品經驗與早期內容建構優勢相關的探索性證據」，而非證實先備組具有較高整體能力。

### 3. 學期中的組間趨同

18 位同時具有第一次網頁作業與期末報告的學生中，先備組媒體豐富度平均由 3.23 增至 3.54（+0.31），新加入組由 2.80 增至 3.40（+0.60）。批判反思訊號方面，先備組由 9.72% 增至 12.67%（+2.95 個百分點），新加入組由 7.38% 增至 13.98%（+6.60 個百分點）。

至期末，兩組在媒體與反思訊號上的差異較早期縮小。這與「先備經驗帶來的早期差距，在共同的 AI 輔助網頁製作經驗累積後逐步縮小」的描述一致，但由於第一次作業與期末報告目的不同，不能將其視為等值前後測。

**[Figure 2 建議：先備組與新加入組由第一次網頁作業至期末的媒體豐富度與批判反思訊號平均軌跡]**

---

## 四、討論與結論

本研究顯示，連續使用生成式 AI 與網頁部署工具的地球科學課程中，學生數位作品最一致的變化出現在媒體整合與內容產出。另一方面，已有前一學期數位作品紀錄的學生在下一學期早期呈現較完整的內容建構特徵，說明「如何使用 AI 與網頁工具表達科學內容」本身可能是一種可累積的數位經驗。

值得注意的是，新加入組在一學期中的媒體整合與批判反思訊號增幅較大，使兩組到期末時呈現更接近的作品型態。這項結果不應被解讀為 AI 已證實能消除學習落差，但它提出一個值得後續驗證的教育假設：當所有學生持續在相同的 AI-supported authoring environment 中製作、修正與發布作品時，缺乏先備數位經驗的學生可能逐步建立與有經驗者相近的數位表達能力。

本研究有四項主要限制。第一，樣本數小且非隨機分組。第二，「前一學期作品紀錄」只是先備經驗代理變項。第三，不同時間點的作業目的與篇幅要求不同，不能視為標準化前後測。第四，目前數位作品尺規與批判反思訊號主要由規則式方法操作化，後續應加入雙評分者人工評量與 inter-rater reliability，並驗證自動分析與人工評分的一致性。

整體而言，本研究支持將學生數位作品作為觀察 AI 融入科學教育歷程的一種資料來源。相較於只問「AI 是否提高分數」，digital-artifact analysis 能進一步追蹤學生如何逐步整合科學內容、媒體形式與反思表達，並為後續更大樣本與更嚴謹的縱向研究建立分析基礎。

---

## 建議圖表

1. **Figure 1. Longitudinal development of matched students** — 高信度配對學生之媒體豐富度與批判反思訊號個別軌跡。
2. **Figure 2. Prior-experience advantage and convergence** — 先備組與新加入組由第一次網頁作業至期末的兩項平均軌跡。

其餘完整圖表與資料可保留於 GitHub Pages 研究儀表板作補充展示。

---

## 參考文獻（草稿，投稿前依 ASET 格式統一）

- Kasneci, E., et al. (2023). ChatGPT for good? On opportunities and challenges of large language models for education. *Learning and Individual Differences, 103*, 102274.
- Krajcik, J. S., & Blumenfeld, P. C. (2006). Project-based learning. In R. K. Sawyer (Ed.), *The Cambridge Handbook of the Learning Sciences*. Cambridge University Press.
- UNESCO. (2023). *Guidance for Generative AI in Education and Research*. UNESCO.

---

## 投稿措辭守則

### 建議使用

- suggest / indicate / are associated with
- exploratory evidence
- appeared to narrow
- digital-artifact characteristics
- heuristic critical-reflection signal

### 避免使用

- prove / demonstrate causal effect
- AI significantly improved learning ability（除非另有正式推論檢定與等值測量）
- low-achieving students（目前沒有正式低成就分組變項）
- AI eliminated the achievement gap
