/**
 * Bot Item Marker — 在物品名稱前後加上彩色標記符號
 * 
 * 用途：讓 bot 用 template matching 精準偵測地上物品
 * 原理：遊戲中不會自然出現亮綠色【】，所以 false positive = 0
 */

const color = config.markerColor;   // e.g., "ÿc2" (亮綠)
const left = config.markerLeft;     // e.g., "【"
const right = config.markerRight;   // e.g., "】"
const reset = "ÿc0";               // 重置為白色（物品原本顏色）

// 所有語言欄位
const LANGUAGES = [
  "enUS", "zhTW", "zhCN", "deDE", "esES", "esMX",
  "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU"
];

// 讀取物品名稱表（用正斜線）
const filePath = "local/lng/strings/item-names.json";
const itemNames = D2RMM.readJson(filePath);

if (itemNames == null) {
  D2RMM.error("無法讀取 " + filePath);
} else {
  // 遍歷每個物品，加上標記
  for (const entry of itemNames) {
    for (const lang of LANGUAGES) {
      if (entry[lang]) {
        entry[lang] = color + left + reset + " " + entry[lang] + " " + color + right;
      }
    }
  }

  // 寫回
  D2RMM.writeJson(filePath, itemNames);
}
