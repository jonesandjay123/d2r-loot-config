/**
 * Bot Item Marker — 在物品名稱後面加上紫色§標記
 * §放後面，不影響物品原本顏色
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
        // 原本物品名 + 空格 + 紫色§（放後面不影響原色）
        entry[lang] = entry[lang] + " " + "ÿc;" + "§";
      }
    }
  }
  D2RMM.writeJson(filePath, itemNames);
}
