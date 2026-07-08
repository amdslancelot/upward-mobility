# 三種 model × 三種工具的影響評估

撰寫：2026-07-08（原版）；2026-07-08 Fable 5 重評估（本版）。
資料來源：Fable 5 純推理，無工具呼叫。

前提說明：session 開頭注入（~600 token）會進 prompt cache，重播按 cache-read 計價約原價 10%。固定注入的**錢**幾乎可忽略。真正的決策變數是三個：**輸出壓縮的實際價值、context 增長速度、注意力稀釋對行為的影響**。

模型費率參考（API 牌價，input/output，每百萬 token，2026-07 版本）：

| 模型 | Input | Output |
|---|---|---|
| Fable 5 | $10 | $50 |
| Opus 4.8 | $5 | $25 |
| Sonnet 4.6 | $3 | $15 |

---

## 一、Caveman 模式

**主張**：壓縮 Claude chat 輸出 ~75%，節省 output token。

### 對 Sonnet 4.6

**實際效益：高。**

Sonnet 是三者中天然輸出最囉嗦的——愛鋪陳、愛總結、愛加免責段落——壓縮率最接近標稱 75%。輸出費率雖最低（$15/M），主要收益來自 **context 增長變慢**：assistant 訊息變短 → 後續每輪重播的 input 也變小，長 session 有複利效果。

注意：Sonnet 指令遵循餘裕最緊，同時維持 fragment 句式 + 技術準確度，偶爾犧牲細節精度。可接受的代價。

結論：Sonnet + Caveman = 正收益，**always-on**。

### 對 Opus 4.8

**實際效益：高，品質代價最低。**

Opus 的冗長集中在「解釋與論證」，壓縮空間大。關鍵優勢：Opus 推理主要發生在 extended thinking 內，Caveman 只壓縮**對話輸出**，不碰思考過程，壓縮不傷推理品質。$25/M 輸出價 × 高壓縮率，是三個模型中「省錢 × 零品質代價」乘積最好的一格。

結論：Opus + Caveman = 最安全的壓縮，**always-on**。

### 對 Fable 5

**實際效益：中低。**

Fable 5 的預設輸出已偏精簡，標稱 75% 壓縮率在它身上實際估計只有 30–50%。輸出單價 $50/M 最高，每省一個 token 值最多，淨值仍為正——但遠低於宣傳值。每訊息 50 token hook 在超長 session 累積後，配上 $10/M 的 input 價是三者中最貴的注入成本。

結論：Fable 5 + Caveman = **按需或 lite 檔**，不需要 always-on；主要理由若有是 context 節省而非風格矯正。

---

## 二、Ponytail 模式

**主張**：YAGNI 強制執行，最短 diff，梯子法篩解法。

### 對 Sonnet 4.6

**實際效益：最高（全場最大邊際效果）。**

Sonnet 是三者中過度工程傾向最強的：投機性抽象、單一實作配 interface、「以後可能用到」的 scaffolding、每個 caller 各補一個 guard——Ponytail 梯子法直接打擊這些目標。更短的 diff 對 Sonnet 有第二層效益：寫得越少，犯錯面越小。

唯一風險：Sonnet 可能把「lazy」執行過頭、跳過理解直接給最小 diff——「先讀完再懶」這條對 Sonnet 約束力最弱，需要在 prompt 中明確強調。

結論：Sonnet + Ponytail = **強烈推薦 always-on**。

### 對 Opus 4.8

**實際效益：高。**

Opus 的問題不是能力不足，是**太完整**：傾向交付含設計文件氣質的全套方案。Ponytail 對它是範圍上限器（scope cap），且 Opus 的推理深度足以真正執行梯子法判斷——「這需要存在嗎」對弱模型是口號，對 Opus 是可以認真回答的問題。

結論：Opus + Ponytail = **推薦 always-on**。

### 對 Fable 5

**實際效益：中，主要價值在防漂移。**

梯子法大部分與 Fable 5 的預設重疊，單次任務邊際效果中等。but always-on 的價值在**長 session 的漂移防護**：沒有持續約束時，任何模型在第 30 輪之後都會慢慢滑回過度建設。純經濟帳：diff 每短 1,000 token，在 Fable 5 省 $0.05 輸出費，是三者中絕對省最多的。

文件/知識類任務注意：Ponytail 壓力可能悄悄砍掉理由句與澄清段——這類任務可考慮暫停。

結論：Fable 5 + Ponytail = **推薦 always-on**，文件任務視情況暫停。

---

## 三、Skills 清單（常駐描述的 context 成本）

所有 skill 描述在每個 session 自動載入（不管有無使用），估計 ~4–5 KB。快取後錢的成本幾乎歸零。真正的成本是**注意力稀釋**：二十幾條觸發條款對每一輪決策的干擾——越弱的模型傷越重。

### 對 Sonnet 4.6

**影響：注意力稀釋最嚴重。**

Token 成本最低（$3/M），不是問題。但 Sonnet 指令遵循餘裕最緊，二十幾個 skill 描述中帶攻擊性觸發條款的那幾條，最容易造成誤觸發或漏觸發。收益端反而最高：skills 封裝了 Sonnet 自己不具備的專家知識（設計哲學、humanizer 模式）和 harness 操作（update-config、schedule）。

結論：**推薦保留，但最值得修剪的就是這一格**。砍掉三個月沒用過的 skill，把觸發條款比本體長的描述瘦身。

### 對 Opus 4.8

**影響：中，注意力稀釋抵抗力強。**

Token 成本可忽略，注意力稀釋抵抗力強。知識型 skill（設計哲學）對 Opus 邊際價值低，自己就懂大半；能力閘門型 skill（harness 設定、排程）不管模型多強都必須靠描述才知道存在。四條重疊 review 路徑在 Opus 上觸發衝突反而最嚴重——Opus 容易「誰看起來最像就用誰」。

結論：**推薦保留，清除重疊 review 路徑**。

### 對 Fable 5

**影響：注意力稅，不是 token 稅。**

$10/M input × 4–5 KB ≈ 快取後不到一分錢/session，錢不是問題。問題是像 `claude-api` 那種觸發條款比本體還長的描述，對任何模型都是純注意力稅。低品質描述（如 `emil-design-eng` 無觸發詞）帶來靜默失效——技能存在但永遠不被叫到。

結論：**推薦保留，修剪低品質描述與過長觸發條款**。

---

## 綜合評估表

| | Caveman | Ponytail | Skills 清單 |
|---|---|---|---|
| **Sonnet 4.6** | ✓ always-on — 壓縮率最接近標稱，context 節省複利最大 | ✓✓ always-on — 過度工程傾向最強，約束效果全場最大 | 推薦但修剪——知識型 skill 對它價值最高，注意力稀釋也傷它最重 |
| **Opus 4.8** | ✓ always-on — 不碰 thinking，品質零代價，省錢效率最佳 | ✓ always-on — 「太完整」天性需要範圍上限器 | 推薦——成本可忽略，清除重疊 review 路徑 |
| **Fable 5** | 按需或 lite — 天然已精簡，實際壓縮遠低於 75% | ✓ always-on — 長 session 防漂移；$50/M 使 diff 節省絕對值全場最高 | 推薦但修剪——注意力稅才是問題，砍低品質描述 |

---

## 行動建議

1. **Ponytail 三個模型全部 always-on。** 600 token 固定成本走快取後幾乎歸零；約束效益在每個模型都是正收益，且模型越貴省越多。這是三個工具中唯一無條件推薦的。
2. **Caveman：Sonnet/Opus always-on，Fable 5 降為按需（或 lite 檔）。** 壓縮工具的價值與模型天然囉嗦度成正比；對已精簡的模型，always-on 的唯一剩餘理由是 context 節省，按需開就夠。
3. **用注意力預算（不是 token 預算）修剪 Skills 清單。** 快取讓 4–5 KB 的錢近乎歸零；真正的成本是觸發條款對每一輪決策的干擾——砍掉長期未用的 skill，把觸發條款比本體長的描述瘦身，對 Sonnet 收益最大。
