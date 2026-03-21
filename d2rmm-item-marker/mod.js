/**
 * Bot Item Marker — 在物品名稱前加上紫色§標記
 * 物品名本身保持原色（暗金/綠/藍等不受影響）
 */

const LANGUAGES = [
  "enUS", "zhTW", "zhCN", "deDE", "esES", "esMX",
  "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU"
];

const filePath = "local/lng/strings/item-names.json";
const itemNames = D2RMM.readJson(filePath);

if (itemNames == null) {
  D2RMM.error("Cannot read " + filePath);
} else {
  for (const entry of itemNames) {
    for (const lang of LANGUAGES) {
      if (entry[lang]) {
        // 紫色§ + 空格 + 原本物品名（不加 reset，讓物品保持原色）
        entry[lang] = "ÿc;" + "§" + " " + entry[lang];
      }
    }
  }
  D2RMM.writeJson(filePath, itemNames);
}
