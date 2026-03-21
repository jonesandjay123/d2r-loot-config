/**
 * Bot Item Marker — 在物品名稱前加上紫色§標記
 * 
 * 用途：讓 bot 用 template matching 精準偵測地上物品
 * 原理：遊戲中不會自然出現紫色§，false positive = 0
 */

const color = config.markerColor;     // "ÿc;" (紫色)
const symbol = config.markerSymbol;   // "§"
const reset = "ÿc0";                 // 重置為物品原本顏色

// 所有語言欄位
const LANGUAGES = [
  "enUS", "zhTW", "zhCN", "deDE", "esES", "esMX",
  "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU"
];

// 讀取物品名稱表
const filePath = "local/lng/strings/item-names.json";
const itemNames = D2RMM.readJson(filePath);

if (itemNames == null) {
  D2RMM.error("無法讀取 " + filePath);
} else {
  for (const entry of itemNames) {
    for (const lang of LANGUAGES) {
      if (entry[lang]) {
        // 紫色§ + 重置色 + 空格 + 原本物品名
        entry[lang] = color + symbol + reset + " " + entry[lang];
      }
    }
  }
  D2RMM.writeJson(filePath, itemNames);
}
