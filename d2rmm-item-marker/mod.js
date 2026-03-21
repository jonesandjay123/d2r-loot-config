/**
 * Bot Item Marker — 在物品名稱前加上紫色§標記
 */

const color = "ÿc;";    // 紫色
const symbol = "§";
const reset = "ÿc0";    // 重置色

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
        entry[lang] = color + symbol + reset + " " + entry[lang];
      }
    }
  }
  D2RMM.writeJson(filePath, itemNames);
}
