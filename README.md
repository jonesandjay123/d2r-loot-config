# D2R Loot Config

D2R PixelBot 的遠端撿寶策略設定。

Bot 每輪 run 開始前會從此 repo 的 `loot_filter.json` 讀取最新設定。
修改 JSON → push → 下一輪自動生效，不需要重啟 bot。

## 使用方式

1. 編輯 `loot_filter.json`（GitHub 網頁 / 手機 / Jarvis 幫改）
2. Commit & Push
3. Bot 下一輪自動讀取新設定

## 架構

```
你（手機/電腦/跟 Jarvis 說）
       │
       ▼
  編輯 loot_filter.json → push to GitHub
       │
       ▼
  Bot GET raw.githubusercontent.com/.../loot_filter.json
       │
       ├→ 成功 → 用遠端設定（同時更新 local cache）
       └→ 失敗 → 用本地 fallback（上次成功的版本）
```

## JSON 欄位說明

### 頂層

| 欄位 | 說明 |
|------|------|
| `version` | 版本號，方便 debug 確認 bot 用到哪個版本 |
| `kill_switch` | `true` = 停止所有撿寶（安全開關） |

### pickup_by_color

控制哪些顏色的物品要撿：

| 顏色 | 說明 | 遊戲內顯示 |
|------|------|-----------|
| `gold` | 暗金（Unique） | 🟤 深金色 |
| `green` | 套裝（Set） | 🟢 綠色 |
| `orange` | 符文/工藝（Rune/Crafted） | 🟠 橘色 |
| `yellow` | 稀有（Rare） | 🟡 黃色 |
| `blue_special` | 藍色符咒/珠寶 | 🔵 藍色（特殊） |
| `white_special` | 活力藥水/寶石 | ⚪ 白色（特殊） |

### yellow.filter

黃色物品的進階過濾：

| mode | 效果 |
|------|------|
| `all` | 撿所有黃色物品 |
| `whitelist` | 只撿 `whitelist` 清單內的類別 |
| `none` | 完全不撿黃色 |

whitelist 可用值（未來擴充）：
`ring`, `amulet`, `gloves`, `boots`, `circlet`, `belt`, `armor`, `weapon`, `helm`, `shield`

### sell_by_color

控制哪些顏色的物品要賣掉。黃色珠寶/戒指/護身符透過 template matching 保護不賣。

### kill_switch 緊急開關

如果你手滑改壞 JSON 或想立刻停止撿寶：
```json
"kill_switch": true
```
Bot 會跳過所有撿寶，只做 run（殺怪 + 存檔），不撿任何東西。

## 注意事項

- ⚠️ JSON 格式錯誤時 bot 會 fallback 到本地設定，不會崩潰
- ⚠️ 不要在此 repo 放任何私人資訊（路徑、IP、帳號、截圖）
- 版本號建議每次修改 +1，方便追蹤

## 未來規劃

- [ ] Phase 2: 物品名稱白名單（利用 CASC zhTW 字典）
- [ ] Phase 3: OCR 文字辨識 + fuzzy match
- [ ] Phase 4: 手機友善的編輯 UI
