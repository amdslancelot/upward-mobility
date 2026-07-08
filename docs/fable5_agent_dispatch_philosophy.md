# 派工決策的運作原理與哲學（Fable 5 session 實錄）

> 撰寫：2026-07-06。本檔整理自 Fable 5 session 中關於「模型如何決定派工」的討論，
> 含機制解析與本 session 的實測數據。讀者：之後的主對話模型與使用者本人。

## 一、誰在做決定：harness 是水管，模型是唯一的決策者

使用者訊息裡的「use only claude-haiku-4-5-20251001 model」對 Claude Code CLI 而言只是普通文字 — CLI 不解析、不路由。唯一能讀懂並執行這個指令的是主對話模型（由 /model 設定決定，本 session 為 Fable 5）。

「主對話模型思考」本身就是一次遠端 API 呼叫，沒有本地推理。CLI（本機程式）只做機械工作：跑 hooks、組 payload（system prompt + CLAUDE.md + 記憶 + 對話歷史 + 使用者訊息）、送 API、渲染輸出、執行 tool call。

## 二、派工決定的機械形式

每個 turn 只有一次主模型 inference。「派工」與「不派工」的差別，只是這次 inference 最後生成的內容：

- 不派 = 輸出純文字。共 1 次遠端呼叫，turn 結束。
- 派 = 輸出一個 Agent tool_use block（含 subagent_type、model、交辦 prompt）。CLI 攔截後發起第二次呼叫給指定的便宜模型，subagent 自己跑多輪，收工後回報再回灌主模型收尾。共至少 3 次遠端呼叫。

「決定不派」不會留下任何 API 痕跡 — 它只表現為「少了一次呼叫」。決定與作答發生在同一串 token 生成裡，沒有獨立的路由器或決策模組。

## 三、成本結構真相（本 session 實測）

haiku 派工的固定成本約 20k tokens/次（實測 7 次 haiku 派工：18.3k–26.9k，平均約 20.8k），成本來自冷啟動：subagent 要載入自己的 system prompt、讀檔重建脈絡、多輪執行。

兩種情境的單次 prompt 成本結構：

| 項目 | 不派工 | 成功派工 |
|---|---|---|
| 主模型呼叫次數 | 1 | 2（寫交辦 prompt；讀回報收尾）|
| 主模型 output | 純答案（短）| 交辦 prompt 常比純答案更長（含內容與驗收條件）|
| 主模型 input | 完整 context ×1 | 完整 context ×2 |
| 便宜模型 | 0 | 約 20k |

三個推論：

1. 派工不省主模型的 output，常常反而更多 — 交辦 prompt（背景+內容+驗收）比直接回答長。省的是「執行迴圈」：subagent 讀檔、修改、重試的多輪全算在便宜模型頭上。
2. 所以判準是任務的「執行輪次」不是「難度」：多輪機械執行（改檔、掃描、驗證）→ 派工划算；一句話能答的（尤其答案已在主模型 context 裡的指涉、澄清、判斷題）→ 派工是純浪費，且 fresh-context subagent 需要的背景說明往往等於把答案先寫一遍。
3. 主模型 input 兩種情境幾乎一樣（整個 context 重送），差額由 prompt cache 吸收（實測某輪：cache 命中 113,846 tokens vs 新 input 76 tokens）。

## 四、本 session 派工實錄（subagent tokens 為 usage 回報精確值）

| 任務 | model | tokens |
|---|---|---|
| Repo 掃描 | sonnet | 16,298 |
| Claude Code 文件查證 | （agent 預設）| 29,109 |
| 制度檔對抗審查 | sonnet | 36,554 |
| 制度檔 read-back | haiku | 26,973 |
| worklog 追加（session 總結）| haiku | 18,881 |
| Worker 必要性作答 | haiku | 19,358 |
| Supabase Storage 查證 | haiku | 21,304 |
| worklog 追加（worker 討論）| haiku | 18,253 |
| worklog 追加（Storage）| haiku | 21,127 |
| worklog 追加（估算）| haiku | 19,989 |

haiku 合計 145,885；sonnet 合計 52,852。

## 五、字面指令 vs 意圖：偏離要揭露

使用者指令「use only haiku」的意圖是省貴模型額度。當字面照做反而更貴（例：一句話的澄清題，派工 20k vs 直接答數百 token），主模型應照意圖處理 — 但必須在回覆中明確揭露「沒派、為什麼」，讓使用者有機會 override。使用者在知情後仍堅持字面指令時，照辦，不再重複論證。

## 六、token 計量的數據源（模型看不到自己的用量）

1. Session log：~/.claude/projects/<專案>/<session-id>.jsonl，記錄每次 API 呼叫的 input_tokens / cache_creation_input_tokens / cache_read_input_tokens / output_tokens 與 model 欄位。caveman-stats 與第三方工具（ccusage）都是讀這個檔加總。
2. 內建指令（使用者直接打，不耗模型 token）：/cost（session 統計）、/context（context 組成）、/usage（訂閱額度，較新版本才有）。
3. 派工回報：每個 subagent 收工附 usage 區塊。
4. 權威對帳：Anthropic usage 儀表板 — 訂閱額度對 cache 命中與不同模型的折算規則未公開，只有儀表板準。

主對話模型自己看不到自己的計量，要知道就得讀 log 檔或請使用者打 /cost。

## 七、無狀態 API：「完整呼叫」的解剖

API 是無狀態的 — 伺服器不保存對話。「主對話模型記得前面說過什麼」的唯一原因，是本機 CLI 把整場對話每次都物理性重送。一次呼叫的 payload：

| 區塊 | 內容 | 量級（本 session 實測時點）|
|---|---|---|
| System prompt | harness 指令 + CLAUDE.md + 記憶索引 + hook 注入 | 約 20–30k tokens |
| Tool 定義 | 每個工具的 JSON schema | 數千 |
| 完整對話歷史 | 所有訊息 + 過去所有 tool_use 與 tool result | 隨 session 成長 |
| 新增量 | 使用者新訊息，或上一個 tool 的執行結果 | 幾十到幾千 |

一個 turn 內跑 N 個 tool call = N+1 次 API 呼叫，每次都重送以上全部。模型每次呼叫都是「失憶重生」；上一輪的輸出（含 tool_use）成為下一輪的 input — 這是「來回都算 token」的機制原因。

Cache 的作用位置：伺服器把「與上次完全相同的前綴」快取（預設 TTL 5 分鐘），重送的舊前綴按 cache read 計價（API 牌價約 0.1 倍 input 價），只有尾端新增部分全價，且新增部分寫入 cache 另收 1.25 倍（5 分鐘 TTL）。實測某輪：cache read 113,846 tokens、新 input 76、cache 寫入 2,779、output 987。

所以每輪的成本結構 = 重送全部（舊的 0.1 倍）+ 新增量全價 + 寫 cache 1.25 倍 + output 全價。單輪不貴；貴的是「新增量 × 之後每輪都變成要重送的歷史」的累積 — 把大量原料放進主 context 的行為在複利計息。

## 八、修正後的派工判準（含 context 複利因素)

「cache 命中很便宜，所以主模型自己做更省」只對一半。cache 省的是「重讀舊 context」，省不了兩樣東西：

1. **執行輪次的費率差**：主模型自己跑 4 輪 tool call = 4 次完整呼叫全按主模型費率；同樣的事讓 haiku 跑 = 全按 haiku 費率。API 牌價（2026-06 快取版，訂閱折算未公開）：Fable 5 $10/$50、Opus 4.8 $5/$25、Sonnet 4.6 $3/$15、Haiku 4.5 $1/$5（每百萬 token，input/output）— 主模型與 haiku 差 10 倍。
2. **永久性 context 污染**：主模型自己讀的檔案內容永遠留在主 context，之後每輪重付（cache read 不是免費），還提早吃滿 context window。派工時原料只活在 subagent 的短命 context，回灌主對話的只有壓縮結論。

判準表（取代單純的「派工省錢」直覺）：

| 任務型態 | 正解 | 理由 |
|---|---|---|
| 答案已在主模型 context 裡（指涉、澄清、判斷）| 主模型直接答 | 0 輪執行，派工 = 純付 20k 冷啟動 |
| 1–2 輪、產物短（單檔小 edit）| 兩可，偏直接做 | 省的輪次蓋不過冷啟動 |
| ≥3–4 輪執行、或要讀大量原料 | 派工 | 輪次費率差 + context 污染複利，20k 很快回本 |

## 九、/compact 與 /clear：context 的重置手段

`/compact`：花一次貴呼叫把歷史壓成摘要，之後每輪改送「摘要 + 近期訊息」。代價是失真 — 行號、路徑、原文錯誤訊息、數字常在摘要中消失。規則：

1. **先存檔再壓**：結論寫進檔案後 compact 才是零損失（「隨做隨寫」規則的另一個理由）。
2. **壓在任務邊界**，不壓在任務進行中。context 快滿時系統會自動 compact，但自動觸發不挑時機 — 手動壓在好時機優於被動。
3. 可帶指示：`/compact 保留所有檔案路徑、行號、未完成事項`。

`/clear`：歸零，零成本。下一個任務與現在**不相關**時用它 — 新 session 從 CLAUDE.md 索引（56 行）+ worklog 重建，比 compact 摘要更便宜也更準。

一句話判準：**同一件事沒做完 → /compact；換一件事 → /clear。** 這兩個指令都是使用者打的（模型無法自行觸發 /clear；長對話時模型能做的是提醒使用者）。

Cache TTL 附註：5 分鐘內連續操作 cache 熱；隔超過 5 分鐘回來，整段前綴要重新寫入 cache（1.25 倍）。意識到即可，不要為了 TTL 扭曲工作節奏。
