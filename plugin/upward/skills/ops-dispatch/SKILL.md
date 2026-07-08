---
name: ops-dispatch
description: 派工守則與 prompt 範本。要把工作交辦給 subagent 時用：怎麼選 agent type 與 model、交辦必含的三要素、haiku→sonnet→opus 升降級路徑、驗證不自驗規則、以及搜尋/實作/重構/研究/審查/貼檔六種可直接抄的 prompt 範本。Use before delegating any task to a subagent.
---
# 模型調度守則

> 讀者：主對話的模型（任何等級）。目的：讓便宜模型跑日常、貴模型只花在判斷上。
> 「查證過的可用資源」節必須在採用時重新查證並更新查證日期 — 不要沿用模板裡的值。

## 查證過的可用資源（2026-07-07 查證於官方文件 — 過期先重查再用）

- 主對話切換型號：`/model <alias>`。alias：haiku / sonnet / opus / fable。能力/成本排序 haiku < sonnet < opus < fable。
- 現役模型 ID（2026-07-07，platform.claude.com models overview）：claude-haiku-4-5-20251001、claude-opus-4-8、claude-fable-5 現役；claude-sonnet-4-6 已列 legacy，官方文件標現役最新 Sonnet 為 claude-sonnet-5。**alias `sonnet` 在你的 harness 實際對應哪版未逐環境確認 — 用 `/model` 介面看，不要沿用本行。**
- Agent tool 的 `model` 參數收上述 alias（sub-agents 官方文件確認）。
- Effort：Agent tool 呼叫本身沒有 effort 參數；只能在 `.claude/agents/*.md` frontmatter 設 `effort: low|medium|high|xhigh|max`。注意 Sonnet 4.6 / Opus 4.6 無 xhigh；Fable 5、Sonnet 5、Opus 4.8/4.7 有完整五級（2026-07-07 查證於 model-config 官方文件）。
- Thinking 控制：settings.json `alwaysThinkingEnabled`、env `MAX_THINKING_TOKENS`（Fable 5 無法關 thinking）。
- 本環境特有 agent types（2026-07-07 實測存在）：caveman:cavecrew-investigator / cavecrew-builder / cavecrew-reviewer（壓縮輸出省主 context）。移植到沒裝 caveman plugin 的環境時，用 Explore / general-purpose 替代。

## 鐵律：指揮官不下場

主對話不做：大量讀檔、掃 repo、查網頁、批次改檔、跑驗證。這些派 subagent，主對話只收結論。主對話只做：拆任務、下判斷、整合結論、跟使用者對話。

## 派工對照表

| 任務 | agent type | model | 理由 |
|---|---|---|---|
| 找定義/呼叫點/檔案位置 | caveman:cavecrew-investigator（無則 Explore） | haiku | 純檢索 |
| 廣域搜尋、不確定在哪 | Explore | sonnet | 需要一點推理選路 |
| 1–2 檔的機械修改 | caveman:cavecrew-builder（無則 general-purpose） | sonnet | 範圍已知，照做即可 |
| 跨檔實作、新功能 | general-purpose | sonnet | 需要理解 + 實作 |
| Diff review | /code-review skill 或 caveman:cavecrew-reviewer（無則 general-purpose） | sonnet | 一行一 finding |
| 架構取捨、模糊需求拆解 | 主對話自己做，或 Plan agent | opus | 換便宜模型就掉品質的部分 |
| 驗證別人的產出 | general-purpose（新開，不續用做事者）| haiku/sonnet | 見「驗證不自驗」 |

## 任務交辦三要素（每次派工必含，缺一不派）

1. **目標與動機**：做什麼、為什麼（subagent 沒有你的對話脈絡，一句動機能避開一半的誤解）。
2. **驗收條件**：可判定的完成標準（「測試 X 通過」「回報含 file:line」），不是「做好」。
3. **回報格式**：subagent 只回結論與 `檔案:行號`；長產物（>50 行）寫到檔案回傳路徑。原始碼全文、完整 log 不准貼回來。

範本見 `ops-dispatch skill`。交辦「貼內容進檔案」的任務時：內容邊界用 code fence 包住並明說 fence 不是內容；驗收條件加「grep 邊界標記在目標檔為 0 hits」（血淚教訓：builder 會把分隔標記貼進檔案）。

## 升降級路徑

- **haiku 錯一次** → 同任務升 sonnet 重派，prompt 附上錯誤輸出。
- **sonnet 同一子任務連錯兩次** → 帶完整失敗軌跡（兩次的 prompt + 錯誤輸出）升 opus。不帶軌跡的升級等於重新賭一次。
- **opus 解出模式後** → 把樣板寫成明確步驟，降回 sonnet/haiku 批次套用。
- **升級前先排除環境／依賴根因**：model 升級治不了壞掉的環境（版本不符、陳舊 build、缺依賴）——這類根因 opus 一樣卡。頑固錯誤先跑 `ops-diagnose skill`#5 的排查清單，再決定要不要升級。
- **同一件事最多重試兩輪**（含升級）。第三輪不是繼續試，是換路或問使用者（判準見 `ops-judge skill`）。

## 驗證不自驗

做的人不驗自己的產出。驗證一律派新開的 subagent（general-purpose，不 SendMessage 續用做事者；下文簡稱 fresh-context）：

- **檔案類**：read-back — 派 haiku 讀檔，回報「存在？涵蓋 X/Y/Z？有無斷句缺漏？」
- **程式碼類**：跑測試或實跑，不接受「看起來對」。
- **高風險判斷**：第二意見 — 另派 agent 對同問題獨立作答比對分歧；或多答案評審擇優。

## 成本直覺（給不確定要不要派工的時刻）

- 派工固定成本 ≈ 20k subagent tokens（冷啟動：載 system prompt、讀檔重建脈絡、多輪執行）。判準是任務的**執行輪次**不是難度：≥3–4 輪 tool call 或要吞大量原料 → 派，划算；答案已在主對話 context 裡的一句話題 → 不派，直接答。
- 交辦 prompt 要把「它需要知道的背景」寫全，別讓它重新探索你已知的事。
- 連續小問題不要每題開新 agent：用 SendMessage 續用同一個 agent（保脈絡、省冷啟動）。

# 任務交辦 prompt 範本

> 用法：主對話派 subagent 時，抄對應範本填空。`[ ]` 是必填空格。省略任何一個必填欄就不要派工。
> agent type 與 model 選法見 `ops-dispatch skill` 派工對照表。

## 通用結構（所有範本共用）

```
背景：[一兩句：這個 repo 是什麼、我在做什麼、為什麼需要這個子任務]
任務：[具體要做的事]
範圍：[哪些檔/目錄在範圍內；明確說哪些不要碰]
驗收條件：[可判定的完成標準，逐條]
回報格式：[結論 + 檔案:行號；長產物寫到 (路徑) 回傳路徑；不要貼原始碼全文/完整 log]
```

## 1. 搜尋（investigator/Explore，haiku/sonnet）

```
背景：repo 在 [路徑]，是 [一句話描述]。我需要 [動機]。
任務：找出 [目標：定義/呼叫點/資料流/慣例]。搜這些關鍵詞起手：[詞1, 詞2, ...]。
範圍：[src/ 全部 | 限定目錄]。只讀不改。
驗收條件：每個發現附 檔案:行號；找不到就列出搜過的 pattern 與目錄（證明找過，不是漏找）。
回報格式：file:line 表格，每行一句說明，總長 ≤ 40 行。不要建議修法。
```

## 2. 實作（general-purpose/builder，sonnet）

```
背景：[repo + 功能脈絡]。相關檔案：[檔案清單 + 每個一句話功能]（你——接單的 subagent——先讀完這些再動手；指揮官不必先讀）。
任務：[要實作的行為，含輸入/輸出/邊界情況]。
範圍：預計改 [檔案清單]。要新增檔案先在回報中說明為什麼。不碰 [排除清單]。
慣例：跟隨周邊程式碼的命名與風格；不加新依賴；不做範圍外的重構。
驗收條件：
- [build 指令] 通過（0 error）
- [具體行為驗證：測試 X 綠 / 實跑 Y 路徑輸出 Z]
- diff 只含任務相關改動
回報格式：改了哪些檔（file:line 級別）、驗證怎麼跑的與結果、留下的已知限制。失敗就回報失敗原因與已試方案，不要交「理論上可行」的未驗證碼。
```

## 3. 重構（general-purpose，sonnet；範圍大先派 Plan）

```
背景：[為什麼要重構：重複/耦合/準備 X 功能]。
任務：把 [現狀] 改成 [目標形狀]。行為不得改變。
範圍：[檔案清單]。呼叫端共 [N] 處（先 grep 確認，數字對不上就停下回報）。
驗收條件：
- 重構前先跑一次 [測試/build] 記錄基線，重構後結果與基線一致
- 舊介面呼叫點全部遷移，grep [舊名稱] 為 0 hits
- 無行為變更（不順手修 bug、不順手改格式）
回報格式：遷移對照表（舊→新）、基線比對結果、grep 證據。
```

## 4. 研究（general-purpose + WebSearch，sonnet）

```
背景：[要做的決定] 需要 [哪類事實] 支撐。
任務：查證以下問題：[問題清單]。
來源要求：官方文件/官方 repo 優先；每個事實附來源 URL；查不到就標 UNVERIFIED，禁止用訓練記憶填（特別是版本號、API 參數、價格）。
驗收條件：每個問題都有「答案+來源」或「UNVERIFIED+查過哪裡」。
回報格式：事實清單，每條 ≤ 2 行 + URL。長引文存 [暫存路徑] 回傳路徑。
```

## 5. 審查（reviewer/fresh-context，sonnet）— 類型/model 選法與 prompt 加料見 `ops-review skill`

```
背景：[這個 diff/檔案 是為了什麼]。
任務：審查 [diff 範圍 / 檔案清單]，只找 [正確性 bug | 弱模型會誤讀的模糊句 | 規則互相矛盾 | 過度工程]（選一個焦點，一次審一種）。
驗收條件：每個 finding 一行：位置 + 問題 + 建議修法 + 嚴重度。沒問題的部分不要寫（不要 praise）。
回報格式：finding 清單按嚴重度排序；0 findings 就明說「檢查了 X/Y/Z 面向，無發現」。
特別檢查：[本次特有的風險點]
```

## 6. 追加/貼內容進檔案（builder，haiku）— 含血淚教訓的修正版

```
任務：在 [檔案路徑]（目前 [N] 行）最尾端追加內容。
要追加的內容 = 下方 ```append 圍欄之間的文字。圍欄本身不是內容，不准出現在檔案裡。一字不改，不動既有內容。

```append
[內容]
```

驗收條件（全過才回報成功）：
1. grep 圍欄標記在目標檔為 0 hits。
2. 新內容起始行號 > [N]（確實在尾端）。
3. 既有 1–[N] 行 byte 不變。
回報格式：追加起始與結束行號 + 三條驗收各 PASS/FAIL。
```

## 派工後的主對話義務

- 收到回報先對驗收條件逐條核對，過了才採用；沒過按升降級路徑處理（`ops-dispatch skill`）。
- 回報的行號/數字有矛盾時，主對話必須自己讀檔驗證，再回報使用者。
- 回報裡的結論轉述給使用者時，用完整句子重述，不要原樣轉貼 subagent 的壓縮輸出。
