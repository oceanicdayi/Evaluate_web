# Human validation workflow

這個目錄用來驗證 `Evaluate_web` 的自動化數位作品指標。目標是把目前的規則式分析轉成可由人工評分支持的方法證據。

## 驗證目標

1. 兩位獨立評分者人工評所有可讀作品的：
   - Media Richness（1–4）
   - Layout Structure（1–4）
2. 兩位評分者對分層隨機抽樣句子進行：
   - D = descriptive
   - CR = critical / reflective
   - O = other / non-analytic
3. 先計算人工評分者間信度，再處理 disagreement。
4. 形成 human consensus 後，才比較 human reference 與 Python automated score。

## 盲評原則

正式評分時，評分者不應看到：

- 學期標籤
- prior / new group
- Python 自動評分
- 跨學期配對關係

若原始網址本身暴露學生身分，建議評分者至少對「學期、組別、自動分數」保持盲態。若條件允許，可將作品另存為本機匿名副本或使用中立轉址。

## 建議工作流程

### Step 0 — Calibration

兩位評分者先共同評 3–5 份練習作品。這些作品只用來修訂 `coding_manual.md`，不要納入正式 kappa。

### Step 1 — 準備作品盲評表

建立一份只放在本機、不要 commit 的 `private_artifact_sources.csv`。格式可參考 `private_artifact_sources_template.csv`。

```bash
python human_validation/prepare_artifact_rating.py \
  --input human_validation/private_artifact_sources.csv \
  --output-dir human_validation/private_run
```

會產生：

- `artifact_key.csv`：研究者私有對照表
- `rater_A_artifacts.csv`
- `rater_B_artifacts.csv`

評分者只填：

- `media_score`
- `layout_score`
- notes（可選）

### Step 2 — 抽樣 critical-reflection sentences

私人來源表需含 `stage` 與可讀取的 `source`。預設抽 300 句並盡量平均分配各 stage。

```bash
python human_validation/sample_reflection_sentences.py \
  --input human_validation/private_artifact_sources.csv \
  --output-dir human_validation/private_run \
  --sample-size 300 \
  --seed 20260810
```

會產生：

- `sentence_key.csv`：私有 stage / artifact / automated reference
- `rater_A_sentences.csv`
- `rater_B_sentences.csv`

正式 coding 時只填 `human_code`：`D`、`CR` 或 `O`。

### Step 3 — 計算 inter-rater reliability

```bash
python human_validation/compute_reliability.py \
  --artifact-a human_validation/private_run/rater_A_artifacts.csv \
  --artifact-b human_validation/private_run/rater_B_artifacts.csv \
  --sentence-a human_validation/private_run/rater_A_sentences.csv \
  --sentence-b human_validation/private_run/rater_B_sentences.csv \
  --output-dir human_validation/private_run/reliability
```

輸出包括：

- Media exact agreement
- Media linear / quadratic weighted Cohen's kappa
- Layout exact agreement
- Layout linear / quadratic weighted Cohen's kappa
- Sentence exact agreement
- CR vs non-CR Cohen's kappa
- disagreement CSV

**先算完這一步，再 adjudicate。**

### Step 4 — Adjudication

依 `artifact_disagreements.csv` 與 `sentence_disagreements.csv` 討論差異，建立：

- `consensus_artifacts.csv`
- `consensus_sentences.csv`

不要在計算 inter-rater kappa 前修改原始 A/B 評分。

### Step 5 — Human vs automated validation

若提供 private key 與 consensus：

```bash
python human_validation/compute_reliability.py \
  --artifact-a human_validation/private_run/rater_A_artifacts.csv \
  --artifact-b human_validation/private_run/rater_B_artifacts.csv \
  --sentence-a human_validation/private_run/rater_A_sentences.csv \
  --sentence-b human_validation/private_run/rater_B_sentences.csv \
  --artifact-key human_validation/private_run/artifact_key.csv \
  --sentence-key human_validation/private_run/sentence_key.csv \
  --artifact-consensus human_validation/private_run/consensus_artifacts.csv \
  --sentence-consensus human_validation/private_run/consensus_sentences.csv \
  --output-dir human_validation/private_run/reliability
```

此時才會另外計算 automated vs human consensus 的 agreement、kappa，以及 CR 偵測的 precision / recall / F1。

## 投稿時建議報告

最精簡的寫法可包含：

- Media：quadratic weighted Cohen's κ + exact agreement
- Layout：quadratic weighted Cohen's κ + exact agreement
- Critical-reflection：CR vs non-CR Cohen's κ + exact agreement
- Automated validation：human-consensus vs automated κ；reflection 另報 precision / recall / F1

## 資料安全

`human_validation/.gitignore` 已設定忽略 private source、評分者正式填答、對照表、disagreement 與 reliability 結果。請不要把學生原始網址、姓名、學號、逐句私有文本或對照表 commit 到公開 repository。
