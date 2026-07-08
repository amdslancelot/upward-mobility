# project — CLAUDE.md（索引）

Agent 運作制度包：把高階模型（Fable 5）的判斷外化成便宜模型（Haiku/Sonnet/Opus）能長期照做的規則。本目錄既是可攜模板（複製到其他專案用），也是一個以自身為根目錄的活專案。

**本檔只是索引。只讀你任務需要的那條指到的檔，不要為了「了解專案」整包掃目錄。**

## Session 開始（照順序）

1. 讀本索引，找到任務相關的檔。
2. 使用者第一次用這套制度 → 先讀 `USAGE.md`（workflow 與 prompt 方法）。
3. 派工、升降級、驗證規則 → `ops/model-dispatch.md`。
4. 交辦 prompt 直接抄範本 → `ops/prompt-templates.md`。

## 核心三規則（其餘見各檔）

- **指揮官不下場**：大量讀取/掃描/批次改檔/驗證一律派 subagent，主對話只收結論。
- **驗證不自驗**：完成宣稱必須有執行證據（build/測試/實跑/read-back），驗證派新開的 general-purpose agent（不續用做事者）。
- **卡住的判準查表**：何時升級模型、何時算完成、何時問使用者、何時換路 → `ops/judgment-rubrics.md`。

## 檔案地圖（2026-07-07 查證）

| 檔案 | 內容 | 什麼時候讀 |
|---|---|---|
| `USAGE.md` | 使用者操作手冊：workflow、怎麼下 prompt、模型額度分配 | 使用者問「怎麼用」、session 規劃時 |
| `WEAK-MODEL-PROMPT-GUIDE.md` | 計畫→執行→審查→修訂迴圈的 prompt 骨架＋照做一次的教學範例 | 交辦多產出大任務、要求品質迴圈時 |
| `ops/model-dispatch.md` | 派工對照表、交辦三要素、升降級路徑、驗證不自驗 | 每次派工前 |
| `ops/prompt-templates.md` | 六種交辦範本（搜尋/實作/重構/研究/審查/追加） | 每次派工時抄 |
| `ops/judgment-rubrics.md` | 六組判斷 checklist，每條一正一反例 | 卡住、不確定完成、想升級時 |
| `ops/review-dispatch.md` | 審查怎麼派：四類型、model 選擇、prompt 六要素、findings 處置 | 要派審查/驗證前 |
| `ops/harness-diagnosis.md` | 此 harness 的 token 漏洞與修法 | session 失焦、context 爆炸時 |
| `meta/maintenance.md` | 誰能改什麼、教訓寫回 `meta/lessons.md`、精簡門檻 | 想改制度檔、踩雷後 |
| `meta/letter-template.md` | 交接信骨架 | 重大 session 結束時照它寫 |
| `meta/letter-to-future-sessions.md` | 交接信本體（含最低信心產出清單） | 接手前人工作、想知道哪些數字沒實測時 |
| `meta/AUDIT-2026-07-07.md` | Fable 5 對本制度的審計：能替代到什麼程度、殘餘缺口 | 想知道制度極限、規劃改進時 |
| `meta/CLAUDE.template.md` | 索引骨架（移植到其他專案時用，本專案不讀它） | 只在移植時 |
| `README.md` | 包的內容清單與移植步驟 | 只在移植時 |

重要的「沒有」：本專案無程式碼、無測試、無 build。產物全是 markdown；品質驗證 = fresh-context read-back 與對抗審查（`ops/judgment-rubrics.md`#5）。

## 硬規則

- 寫進檔案的內容（docs/commit）一律完整句子正常寫；壓縮口吻只用於對話。
- 改制度檔前先 git commit（留可回滾點；沒用 git 的專案先 `git init`）；新內容寫新檔；本索引 ≤150 行。
- 目錄約定：根目錄只放使用者直接抄用的入口檔（本檔、USAGE、README、WEAK-MODEL-PROMPT-GUIDE）；工作規則進 `ops/`；制度治理與歷史進 `meta/`。所有檔內路徑一律寫「相對專案根」（例：`ops/model-dispatch.md`），不寫相對自身的 `../`。
- 型號/參數/價格永遠先查證再寫，查不到標 UNVERIFIED，不編造。
- `ops/judgment-rubrics.md` 的規則本體、`.claude/` 設定：動之前先問使用者（詳見 `meta/maintenance.md` 權限分級）。
