# ASET 2026 研究問題與統計分析框架

## 研究定位

本研究將學生在連續地球科學課程中產製的網頁作品視為「數位學習成品（digital artifacts）」，分析學生在 AI 輔助網頁製作環境中的作品發展。

研究重點不是證明 AI 直接提升學科成績，也不把網頁複雜度視為學科能力本身；核心問題是：

1. 同一批學生的數位作品如何隨連續課程經驗改變？
2. 已有前一學期數位作品經驗者，是否在下一學期早期展現先備優勢？
3. 沒有前一學期作品紀錄者，是否在共同課程經驗累積後逐步縮小早期差距？

因此，本研究應定位為 **exploratory longitudinal digital-artifact analysis**，而非隨機控制試驗或 AI 教學的因果效果評估。

---

## 正式研究問題

### RQ1 — Longitudinal development

**在連續兩學期的 AI 輔助地球科學課程中，同一批學生的數位作品在媒體整合、版面結構、可見文本量、學科語言與反思訊號上如何改變？**

主要分析樣本：跨學期高信度配對學生（目前 n = 8）。

主要指標：

- 媒體豐富度（1–4）
- 排版架構（1–4）
- 可見文本字元數
- 專有名詞密度（次／千字）
- 啟發式批判反思訊號（%）

建議統計：

- 個別配對變化圖
- 中位數、平均數與方向性計數（上升／持平／下降）
- 小樣本下以效果方向與個別軌跡為主，不把 p < .05 當作主要論證核心

目前最穩定的描述：

- 媒體整合明顯增加
- 可見文本量整體增加
- 批判反思訊號多數上升
- 排版架構大致持平，可能存在尺規天花板
- 術語密度呈現個別分化

---

### RQ2 — Prior-experience advantage

**已有前一學期數位作品紀錄的學生，是否在下一學期第一次網頁作業中呈現較強的內容建構表現？**

分組：

- 先備組：上學期作品名單內（目前 n = 14）
- 新加入組：未見於上學期作品名單（目前 n = 6）

注意：此分組是「先前作品紀錄」的代理變項，不等同正式修課紀錄、學業成就或隨機分組。

主要指標：

- 可見文本字元數
- 專有名詞絕對次數
- 11 項指定主題涵蓋數
- 媒體豐富度
- 排版架構
- 探索性內容發展指數

建議統計：

- 平均數與中位數
- Cliff's delta
- 精確秩排列檢定
- 高主題涵蓋（>= 8/11）的 Fisher exact test

目前最穩健的描述：

> 先備組在第一次網頁作業中呈現較大的內容量、較多的專有名詞絕對使用次數，以及較完整的指定主題涵蓋；多項內容指標方向一致，形成「先備數位作品經驗與早期內容建構優勢相關」的探索性證據。惟小樣本精確檢定未達顯著，因此不宜宣稱整體作業品質已被證實優於另一組。

---

### RQ3 — Convergence over the semester

**早期與先備經驗相關的差異，是否在一學期共同的 AI 輔助網頁製作經驗後縮小？**

主要樣本：同時具有第一次網頁作業與期末報告的學生（目前 n = 18；先備組 13，新加入組 5）。

主要分析：

- 第一次作業 -> 期末報告的組別平均軌跡
- 個別學生變化
- 媒體豐富度與批判反思訊號的增幅
- 組間 Cliff's delta 在不同階段的變化

目前觀察：

- 新加入組的媒體增幅較大
- 新加入組的批判反思訊號增幅較大
- 到期末時兩組多項指標差距縮小

最穩健的表述：

> Prior digital-artifact experience was associated with an early advantage in content construction, whereas the between-group gap appeared to narrow over the semester as students accumulated shared experience with AI-supported web authoring.

不可使用的因果表述：

- AI 造成新加入組追上先備組
- AI 證實能消除學習落差
- 課程顯著提升低成就學生能力

---

## 指標命名調整

### 1. 「總字數」改稱「可見文本字元數」

程式使用 `len(T)`，計算的是正規化後可見文字的字元數，並非中文斷詞後的 word count。

論文中建議使用：

- 中文：可見文本字元數
- 英文：visible-text character count

### 2. 「批判思考比例」改稱「批判反思訊號」

目前公開結果主要使用關鍵詞啟發式句子分類，因此不能視為經驗證的 critical-thinking scale。

建議使用：

- 中文：啟發式批判反思訊號／批判反思句比例
- 英文：heuristic critical-reflection ratio / critical-reflection signal

### 3. 「媒體／排版分數」明確定義為數位作品尺規

兩者反映作品呈現形式與技術複雜度，不反映地球科學內容正確性。

---

## 投稿前最重要的方法補強

### 人工評分穩定性驗證（已完成）

指導老師對 57 份作品進行兩次盲評（間隔約 30 分鐘），以檢驗媒體豐富度與排版架構尺規的評分穩定性（test-retest reliability）。4 份作品因登入牆或檔案無法存取而排除，最終納入 53 份。

結果：

- 媒體豐富度 quadratic weighted κ=0.750（substantial agreement）
- 排版架構 quadratic weighted κ=0.657（substantial agreement）
- 兩項 within-one agreement 均接近或等於 1.0

此驗證支持尺規在同一評分者重複評分下的穩定性。人工共識與自動化評分的比較顯示，媒體 exact=0.264、排版 exact=0.509，反映自動規則式判定與人工判斷之間存在系統性差異。

批判反思訊號目前僅以關鍵詞啟發式估計，尚未經人工內容分析驗證。論文應將自動尺規稱為 **rule-based operationalization**，並將批判反思比例稱為 **heuristic critical-reflection signal**。

後續研究應：

1. 納入獨立評分者以建立評分者間信度（inter-rater reliability）
2. 修訂編碼手冊以驗證批判反思訊號
3. 擴大樣本驗證自動化尺規與人工評分的對應關係

---

## 建議主要圖表

### Figure 1 — Longitudinal development

高信度配對學生的跨學期個別軌跡，優先呈現：

- 媒體豐富度
- 批判反思訊號

目的：回答 RQ1。

### Figure 2 — Early advantage and convergence

兩組由「第一個網頁作業」到「期末報告」的平均軌跡，優先呈現：

- 媒體豐富度
- 批判反思訊號

目的：同時回答 RQ2 與 RQ3。

其他圖表放研究儀表板或補充資料，不塞入三頁審查短文。

---

## 結論層級

### 可以支持

- 學生作品的媒體整合隨連續課程經驗增加。
- 高信度配對中，多數學生的作品篇幅與批判反思訊號增加。
- 先備數位作品經驗與下一學期早期的內容建構優勢呈方向一致的關聯。
- 新加入組在學期中的部分指標增幅較大，與組間差距逐步縮小的描述一致。

### 目前不能支持

- AI 直接造成學習成效提升。
- AI 提升學科知識正確性。
- AI 對低成就學生特別有效。
- 先備組與新加入組存在已被證實的顯著能力差異。
- 不同作業時間點可以直接視為等值前後測。

---

## 論文核心一句話

> This exploratory longitudinal study suggests that prior digital-artifact experience is associated with an early advantage in scientific content construction, while shared experience with AI-supported web authoring is accompanied by increasingly similar digital-artifact profiles across students over the semester.
