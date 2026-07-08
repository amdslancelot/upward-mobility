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

範本見 `ops/prompt-templates.md`。交辦「貼內容進檔案」的任務時：內容邊界用 code fence 包住並明說 fence 不是內容；驗收條件加「grep 邊界標記在目標檔為 0 hits」（血淚教訓：builder 會把分隔標記貼進檔案）。

## 升降級路徑

- **haiku 錯一次** → 同任務升 sonnet 重派，prompt 附上錯誤輸出。
- **sonnet 同一子任務連錯兩次** → 帶完整失敗軌跡（兩次的 prompt + 錯誤輸出）升 opus。不帶軌跡的升級等於重新賭一次。
- **opus 解出模式後** → 把樣板寫成明確步驟，降回 sonnet/haiku 批次套用。
- **升級前先排除環境／依賴根因**：model 升級治不了壞掉的環境（版本不符、陳舊 build、缺依賴）——這類根因 opus 一樣卡。頑固錯誤先跑 `ops/harness-diagnosis.md`#5 的排查清單，再決定要不要升級。
- **同一件事最多重試兩輪**（含升級）。第三輪不是繼續試，是換路或問使用者（判準見 `ops/judgment-rubrics.md`）。

## 驗證不自驗

做的人不驗自己的產出。驗證一律派新開的 subagent（general-purpose，不 SendMessage 續用做事者；下文簡稱 fresh-context）：

- **檔案類**：read-back — 派 haiku 讀檔，回報「存在？涵蓋 X/Y/Z？有無斷句缺漏？」
- **程式碼類**：跑測試或實跑，不接受「看起來對」。
- **高風險判斷**：第二意見 — 另派 agent 對同問題獨立作答比對分歧；或多答案評審擇優。

## 成本直覺（給不確定要不要派工的時刻）

- 派工固定成本 ≈ 20k subagent tokens（冷啟動：載 system prompt、讀檔重建脈絡、多輪執行）。判準是任務的**執行輪次**不是難度：≥3–4 輪 tool call 或要吞大量原料 → 派，划算；答案已在主對話 context 裡的一句話題 → 不派，直接答。
- 交辦 prompt 要把「它需要知道的背景」寫全，別讓它重新探索你已知的事。
- 連續小問題不要每題開新 agent：用 SendMessage 續用同一個 agent（保脈絡、省冷啟動）。
