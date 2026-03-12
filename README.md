# D2R Loot Config

D2R PixelBot 的物品過濾設定 + 官方 Filter 分析工具。

## 📖 裝備名稱速查表

👉 **[線上版（GitHub Pages）](https://jonesandjay123.github.io/d2r-loot-config/)**

597 個 D2R 物品中英對照，支援搜尋 + 一鍵複製，手機也能用。

## 目前架構（v2.1）

> **2026-03-12 重大改版：** d2r-pixelbot 已完全脫離本 repo 的遠端 config。
> 撿物 = D2R 官方 filter（畫面上看到就撿），賣出保護 = hardcoded in `sell.py`。
> 本 repo 現在的角色是：**官方 filter 備份 + 分析工具 + 裝備速查表**。

```
D2R 遊戲內官方 Filter
       │
       ▼
  遊戲只顯示值得撿的物品（手套/靴/戒指/底材等）
       │
       ▼
  Bot 看到就撿（HSV 偵測）
       │
       ▼
  回城賣出時 → sell.py hardcoded protect 清單保護
       │
       ├→ 黃/金/綠/橘 → 絕不賣
       ├→ 灰/藍/白 → OCR 讀物品名稱 → 比對 protect 關鍵字
       │    ├→ 匹配 → 🛡 不賣
       │    └→ 不匹配 → 💰 賣掉
       └→ 未知 → 不賣
```

## 📂 檔案說明

| 檔案 | 用途 |
|------|------|
| `d2r_official_filter.json` | 遊戲內官方 Filter 設定備份（從遊戲 copy 出來） |
| `parse_filter.py` | 分析工具：翻譯 filter itemCode → zhTW 名稱 + 比對 sell protect |
| `filter_analysis.json` | 分析結果（自動生成） |
| `loot_filter.json` | 舊版遠端撿寶策略（v1.x 用，v2.1 已不讀取） |
| `index.html` | 裝備名稱速查表（GitHub Pages） |

## 🔧 parse_filter.py — Filter 分析工具

解析 `d2r_official_filter.json`，對照 CASC `item-names.json`，輸出：

1. **每條 hide rule 的 zhTW 物品清單** — itemCode → 中文名稱
2. **正向比對** — sell.py protect 清單裡的物品是否被 filter 放行
3. **反向比對** — filter 放行但 protect 沒覆蓋的物品（潛在風險）

### 使用方式

```bash
# 前提：d2r-pixelbot repo 在同目錄下（需要 CASC item-names.json）
cd d2r-loot-config
python parse_filter.py
```

### 更新流程

1. 遊戲內調整 Filter → Export/Copy 到 `d2r_official_filter.json`
2. `git push`
3. 跑 `python parse_filter.py`
4. 看有沒有 ⚠️ 缺口 → 有的話更新 `d2r-pixelbot/bot/sell.py` 的 protect 清單

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

### sell_by_color（v2.1 已不使用）

> ⚠️ v2.1 起賣出邏輯 hardcoded in `sell.py`：灰/藍/白 賣，黃/金/綠/橘 不賣。

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

## ⚠️ 賣出保護架構（v2.1）

### 三層保護機制

```
物品 hover → 「出售價格」template match → 判定顏色
    │
    ├─ 黃/金/綠/橘 → 🛡 第一層：顏色直接保護（絕不賣）
    │
    └─ 灰/藍/白 → 第二層：OCR 讀 tooltip 上下文
         │         （出售價格上方 120px + 下方 46px）
         │
         ├─ OCR 匹配 protect 關鍵字 → 🛡 不賣
         ├─ OCR misread → 第三層：自動修正（寶→賓/實）→ 再比對
         └─ 都沒匹配 → 💰 賣掉
```

### Hardcoded Protect 清單（sell.py）

| 顏色 | 保護關鍵字 |
|------|-----------|
| **yellow** | *(整個顏色不賣，官方 filter 已篩選)* |
| **blue** | 珠寶/珠實/珠賓/咒符/鑲孔 |
| **white** | 活力藥水/全方位活力藥水/寶石/賓石/無瑕 + 符文之語底材（爪/盾/斧/劍/頭盔） |
| **gray** | 骸骨魔杖/君主盾/法師鎧甲/統御者鎧甲 + 符文之語底材（同 white） |

### 容易踩的坑

| 坑 | 解法 |
|----|------|
| OCR 誤讀（寶→賓/實） | `OCR_MISREAD_MAP` 自動修正 + 多關鍵字冗餘 |
| 灰白色判定邊界 | 灰色和白色放同樣的保護詞 |
| 匹配方向 | `保護詞 in OCR名稱`，「無瑕」和「瑕疵」都要放 |
| OCR crop 位置 | 上方 120px + 下方 46px 雙向讀取 |
| 黃色戒指被賣（2026-03-12） | 根本解：黃色從 SELL_COLORS 移除 |

### Debug：物品被意外賣掉

1. 看 log `📖 OCR 讀到:` — OCR 讀到什麼
2. 看 `灰/白消歧義: brightness=XXX` — 顏色判對嗎
3. 看有沒有 `🛡 OCR 保護:` — 有=成功，沒有=匹配失敗
4. 用 `test_sell.py` 模式 7 看 OCR 框框位置
5. 用 `test_sell.py` 模式 8 (dry run) 模擬完整流程

### 維護流程

1. 遊戲內調 filter → copy 到 `d2r_official_filter.json` → push
2. 跑 `python parse_filter.py`
3. 看反向檢查有沒有 ⚠️ 缺口
4. 有缺口 → 更新 `d2r-pixelbot/bot/sell.py` 的 protect 清單
