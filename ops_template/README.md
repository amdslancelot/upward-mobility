# Ops Template Pack — 弱模型可沿用的 agent 運作制度

這是一套可跨專案重複使用的 Claude Code（或同類 agent harness）運作制度模板。
原版由一次高階模型（Fable 5）session 建立，目的：把高階判斷外化成便宜模型也能長期照做的規則。

本目錄同時是**一個以自身為根的活專案**：`CLAUDE.md` 是本目錄的實際索引（session 會載入），
`USAGE.md` 是使用者操作手冊，`meta/AUDIT-2026-07-07.md` 是 Fable 5 對這套制度的能力審計。
`meta/CLAUDE.template.md` 只在移植到其他專案時使用。

## 這包裡有什麼

| 檔案 | 內容 | 採用時要做什麼 |
|---|---|---|
| `meta/CLAUDE.template.md` | 專案索引骨架（≤150 行，只當路由） | 填 `{{...}}` 佔位符，改名為專案根目錄的 `CLAUDE.md` |
| `ops/harness-diagnosis.md` | 環境陷阱與修法（token 漏、主對話下場、context 複利） | 第 0 節有「重新診斷你自己環境」的步驟，照做後改寫環境特定段 |
| `ops/model-dispatch.md` | 派工對照表、交辦三要素、升降級路徑、驗證不自驗 | 重新查證「可用資源」節的型號與參數（有查證日期標記） |
| `ops/judgment-rubrics.md` | 六組判斷 checklist，每條一正一反例 | 直接可用；把範例換成你專案的實例更好 |
| `ops/prompt-templates.md` | 搜尋/實作/重構/研究/審查/追加六種交辦範本 | 直接可用 |
| `meta/maintenance.md` | 權限分級、教訓格式、精簡門檻、健檢清單 | 填佔位符 |
| `meta/letter-template.md` | 「給未來 session 的交接信」骨架 | 每次重大 session 結束時照骨架填寫 |
| `USAGE.md` | 使用者操作手冊：workflow、prompt 方法、額度分配 | 直接可用；模型 alias 相關段落隨查證日期更新 |
| `meta/AUDIT-2026-07-07.md` | 制度能力審計：可替代程度、弱指揮官失效模式 | 參考文件；移植時可不帶 |

## 採用步驟（在新專案照順序做）

1. 把整個資料夾（含 `ops/`、`meta/` 子目錄）複製到新專案，例如放 `docs/agent-ops/`。
2. 全域搜尋 `{{` 與 `本環境` 兩個標記，逐一改成新專案的值：`{{制度目錄}}` 填你放的位置（上例為 `docs/agent-ops`）；標「本環境」的段落（記憶目錄路徑、特有 agent types、常駐 plugin）換成新環境實測值。
3. `meta/CLAUDE.template.md` 填完後移到專案根目錄改名 `CLAUDE.md`；程式碼地圖那節派一個便宜 subagent 掃 repo 生成。
4. 照 `ops/harness-diagnosis.md` 第 0 節重新診斷你的環境（plugin、hook、額度方案都可能不同），改寫環境特定段落。
5. 重新查證 `ops/model-dispatch.md` 的型號清單（查官方文件或 harness 環境，不要沿用舊值）。
6. 派一個 fresh-context subagent read-back 全部檔案：路徑都存在？佔位符都填了？規則有沒有互相矛盾？
7. 刪掉本 README 的這一節以上內容或整個 README（採用完就不需要了）。

## 設計原則（改動這套制度前先讀）

- **讀者是弱模型**：規則要具體可執行，附判準與範例；抽象要求等於沒寫。
- **索引與內容分離**：CLAUDE.md 只當路由（≤150 行），長內容放按需讀的檔。常載檔合計 ≤500 行。
- **驗證不自驗**：做的人不驗自己的產出；完成宣稱必須有執行證據。
- **隨做隨寫**：session 隨時可能中斷，存檔的才算數。
- **制度是拿來省判斷的，不是拿來崇拜的**：哪條規則連續三次礙事，帶證據問使用者要不要改。
