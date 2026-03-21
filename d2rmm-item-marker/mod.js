/**
 * Bot Item Marker — 在物品名稱後加上紫色§標記
 * 涵蓋所有物品相關的名稱檔案
 */

const LANGUAGES = [
  "enUS", "zhTW", "zhCN", "deDE", "esES", "esMX",
  "frFR", "itIT", "jaJP", "koKR", "plPL", "ptBR", "ruRU"
];

// 所有可能包含物品名稱的檔案
const FILES = [
  "local/lng/strings/item-names.json",
  "local/lng/strings/item-runes.json",
  "local/lng/strings/item-nameaffixes.json",
  "local/lng/strings/item-modifiers.json",
];

for (const filePath of FILES) {
  const data = D2RMM.readJson(filePath);
  if (data == null) {
    D2RMM.warn("Skipped (not found): " + filePath);
    continue;
  }
  
  let count = 0;
  for (const entry of data) {
    for (const lang of LANGUAGES) {
      if (entry[lang] && !entry[lang].endsWith("§")) {
        entry[lang] = entry[lang] + " " + "ÿc;" + "§";
        count++;
      }
    }
  }
  
  D2RMM.writeJson(filePath, data);
  D2RMM.info("Modified " + filePath + " (" + count + " entries)");
}
