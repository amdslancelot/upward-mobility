# Model × Tool 速查表

（Fable 5 重評估版，2026-07-08。詳細推理見長版。）

| | Caveman | Ponytail | Skills 清單 |
|---|---|---|---|
| **Sonnet 4.6** | ✓ always-on | ✓✓ always-on | 推薦，修剪注意力稀釋重的 skill |
| **Opus 4.8** | ✓ always-on | ✓ always-on | 推薦，清除重疊 review 路徑 |
| **Fable 5** | 按需或 lite | ✓ always-on | 推薦，砍低品質描述與過長觸發條款 |

> ✓✓ = 強烈推薦；✓ always-on = 建議常駐；按需 = 不需要常駐，任務需要時開；修剪 = 保留但清理。

## 通用行動（所有模型）

- 刪 `stop-slop`（broken，未被載入）
- 退役 `emil-design-eng`（描述無觸發詞，靜默失效）
- 跑 `caveman-compress` 壓縮 CLAUDE.md（唯一對 input 有確實貢獻的子工具）
- 四路 review 只留：`/code-review`（正確性）+ `ponytail-review`（過度工程）
- Skills 清單用注意力預算修剪，不是 token 預算（快取後錢幾乎歸零）
