/**
 * Bot Item Marker — 在物品名稱後加上§標記
 * § 跟隨物品本身顏色（暗金=金色§，綠裝=綠色§，白裝=白色§）
 * 不使用任何顏色代碼，避免汙染 tooltip
 */

const LANGUAGES = [
  "enUS", "zhTW", "zhCN", "deDE", "esES", "esMX",
  "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU"
];

const FILES = [
  "local/lng/strings/item-names.json",
  "local/lng/strings/item-runes.json",
];

for (const filePath of FILES) {
  const data = D2RMM.readJson(filePath);
  if (data == null) {
    continue;
  }
  
  for (const entry of data) {
    for (const lang of LANGUAGES) {
      if (entry[lang] && !entry[lang].endsWith("§")) {
        // 不加顏色代碼，§ 自然跟隨物品顏色
        entry[lang] = entry[lang] + " §";
      }
    }
  }
  
  D2RMM.writeJson(filePath, data);
}
