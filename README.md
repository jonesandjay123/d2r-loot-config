# D2R Loot Config

D2R PixelBot 的遠端撿寶策略設定。

## 📖 裝備名稱速查表

👉 **[線上版（GitHub Pages）](https://jonesandjay123.github.io/d2r-loot-config/)**

597 個 D2R 物品中英對照，支援搜尋 + 一鍵複製，手機也能用。
用途：編輯 `loot_filter.json` 時快速查詢物品中文名。

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


---

## ⚠️ 保護清單設計指南（重要！）

> **2026-03-06 實戰教訓：無瑕寶石被賣掉事件**

### 事件經過

Bot 撿了無瑕綠寶石，但回城賣物時被賣掉了。

**白色 pickup names 裡有「寶石」，為什麼沒保護到？**

因為 OCR 把「無瑕綠**寶**石」讀成「無瑕綠**賓**石」。`"寶石" in "無瑕綠賓石"` → ❌。

### 保護機制原理

```
物品 hover → 「出售價格」template match → 判定顏色（灰/白/藍/黃）
→ OCR 讀取物品名稱
→ 用 pickup.{判定顏色}.names + sell_protect 做保護清單
→ 保護清單裡任何一個詞 in OCR 讀到的名稱 → 🛡 不賣
→ 沒匹配到 → 💰 賣掉
```

### 三個容易踩的坑

#### 坑 1：OCR 誤讀
EasyOCR 在 D2R 小字體上常見誤讀：

| 正確 | OCR 讀成 | 影響 |
|------|---------|------|
| 寶石 | 賓石、實石 | 「寶石」匹配失敗 |
| 長劍 | 長釗 | 劍類匹配失敗 |
| 闊劍 | 闊釗 | 同上 |

**解法：多個關鍵字冗餘覆蓋。** 「寶石」匹配不到？靠「無瑕」或「瑕疵」當備援。

#### 坑 2：灰白色判定邊界
Bot 根據「出售價格」文字亮度判定灰色 vs 白色：
- 灰色 ≈ 73 brightness
- 白色 ≈ 150 brightness
- 閾值 = 110

便宜白色物品（如寶石）亮度偏低（131-144），偶爾可能被判成灰色。

**解法：灰色和白色的 names 都要放同樣的保護詞。**

```json
"gray": { "names": ["...", "無瑕", "瑕疵", "寶石"] },
"white": { "names": ["...", "無瑕", "瑕疵", "寶石"] }
```

#### 坑 3：匹配方向
規則是 `保護詞 in OCR讀到的名稱`：
- ✅ `"無瑕" in "無瑕綠寶石"` → 匹配！
- ❌ `"瑕疵" in "無瑕綠寶石"` → 不匹配（「瑕疵」≠「瑕」，多一個字）
- ✅ `"瑕疵" in "瑕疵紅寶石"` → 匹配！

**所以「瑕疵」只保護瑕疵級寶石，「無瑕」只保護無瑕級寶石，兩個都要放！**

### 設計保護詞的 Checklist

編輯 `loot_filter.json` 前，確認：

- [ ] 保護詞是物品名稱的**子字串**嗎？（`pname in item_name` 方向）
- [ ] 有沒有**多層冗餘**？（OCR 讀錯一個詞還有別的能救）
- [ ] **灰色和白色**都放了嗎？（灰白判定可能出錯）
- [ ] 2 個字的短詞有沒有搭配更長的詞做**備援**？
- [ ] 用 `test_sell.py` 模式 8 (OCR dry run) **實測過**嗎？

### 當前保護詞範例

**寶石（三重保護）：**
```
「無瑕」→ 保護無瑕XX寶石 ✅
「瑕疵」→ 保護瑕疵XX寶石 ✅  
「寶石」→ 保護所有寶石（OCR 讀對的話）✅
三個詞同時放在 gray + white names 裡
```

**藍色裝備：**
```
「珠寶」→ 保護藍色珠寶 ✅
「咒符」→ 保護藍色咒符 ✅
```

**黃色裝備（全撿 names: "*"）：**
```
sell_protect 裡放手套/靴子/戒指/護身符/珠寶名稱
黃色其他裝備 → 全部賣掉（接受風險）
```

> ⚠️ **2026-03-07 教訓：** v1.7 從 template matching 換成 OCR 時，
> 舊的 `protect_ring.png`、`protect_jewel.png`、`protect_amulet.png` 被移除，
> 但忘了把「戒指」「護身符」「珠寶」加進 `sell_protect`，導致黃色戒指被賣掉。
> **遷移保護機制時，務必確認所有舊保護項都有對應到新機制。**

### Debug：物品被意外賣掉怎麼辦？

1. 看 bot log 的 `📖 OCR 讀到:` — OCR 到底讀到什麼
2. 看 `灰/白消歧義: brightness=XXX → white/gray` — 顏色判對了嗎
3. 看有沒有 `🛡 OCR 保護:` — 有=保護成功，沒有=匹配失敗
4. 確認 `pickup.{顏色}.names` 裡有沒有能匹配的詞
5. 如果是新的 OCR 誤讀 → 加入更多保護詞做冗餘
6. 灰白判錯 → 兩邊都加保護詞
