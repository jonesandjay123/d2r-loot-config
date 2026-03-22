/**
 * Bot Item Marker — 在物品名稱後加上紫色§標記
 * 只改兩個檔案：物品名 + 符文名（不動 modifiers 避免汙染 UI）
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
        entry[lang] = entry[lang] + " " + "ÿc;" + "§" + "ÿc0";
      }
    }
  }
  
  D2RMM.writeJson(filePath, data);
}
