#!/usr/bin/env python3
"""
parse_filter.py — 解析 d2r_official_filter.json，對照 CASC item-names.json，
輸出每條 hide rule 具體隱藏了哪些 zhTW 物品名稱。

用法：
  python parse_filter.py

輸出：
  - 終端顯示每條 rule 的隱藏物品清單
  - 儲存 filter_visible_items.json（被 filter 放行、會顯示在地上的物品）
"""

import json
import os

FILTER_PATH = os.path.join(os.path.dirname(__file__), "d2r_official_filter.json")
CASC_PATH = os.path.join(os.path.dirname(__file__), "..", "d2r-pixelbot", "data", "casc_strings", "item-names.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "filter_analysis.json")


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def build_code_to_name(casc_items):
    """建立 itemCode → zhTW 名稱 mapping"""
    mapping = {}
    for item in casc_items:
        key = item.get("Key", "")
        zh = item.get("zhTW", "")
        if key and zh:
            # 有些 Key 重複（同物品不同 context），取第一個
            if key not in mapping:
                mapping[key] = zh
    return mapping


def analyze_filter(filter_data, code_to_name):
    """分析每條 rule 隱藏了哪些物品"""
    results = []

    for rule in filter_data.get("rules", []):
        name = rule.get("name", "unnamed")
        enabled = rule.get("enabled", False)
        rule_type = rule.get("ruleType", "")

        # 收集這條 rule 涉及的 item codes
        item_codes = rule.get("itemCode", [])
        equip_codes = rule.get("equipmentItemCode", [])
        all_codes = item_codes + equip_codes

        # 對照 zhTW 名稱
        resolved = []
        unresolved = []
        for code in all_codes:
            zh = code_to_name.get(code)
            if zh:
                resolved.append({"code": code, "zhTW": zh})
            else:
                unresolved.append(code)

        # 收集 category / rarity / quality 資訊
        rule_info = {
            "name": name,
            "enabled": enabled,
            "ruleType": rule_type,
            "rarity": rule.get("equipmentRarity", []),
            "quality": rule.get("equipmentQuality", []),
            "categories_hidden": rule.get("equipmentCategory", []),
            "itemCategory_hidden": rule.get("itemCategory", []),
            "filterEtherealSocketed": rule.get("filterEtherealSocketed", False),
            "specific_items_hidden": resolved,
            "unresolved_codes": unresolved,
            "total_codes": len(all_codes),
            "resolved_count": len(resolved),
        }
        results.append(rule_info)

    return results


def print_analysis(results):
    """終端友善輸出"""
    print("=" * 60)
    print("D2R 官方 Filter 分析（zhTW 物品名稱對照）")
    print("=" * 60)

    for i, rule in enumerate(results, 1):
        status = "✅" if rule["enabled"] else "❌"
        print(f"\n{'─' * 60}")
        print(f"規則 {i}: {status} {rule['name']} ({rule['ruleType']})")
        print(f"  稀有度: {', '.join(rule['rarity']) or '(全部)'}")
        print(f"  品質: {', '.join(rule['quality']) or '(全部)'}")
        print(f"  隱藏無形/鑲孔: {'是' if rule['filterEtherealSocketed'] else '否'}")

        if rule["categories_hidden"]:
            print(f"  隱藏裝備類別: {', '.join(rule['categories_hidden'])}")
        if rule["itemCategory_hidden"]:
            print(f"  隱藏物品類別: {', '.join(rule['itemCategory_hidden'])}")

        if rule["specific_items_hidden"]:
            print(f"  額外隱藏的特定物品 ({rule['resolved_count']} 項):")
            for item in sorted(rule["specific_items_hidden"], key=lambda x: x["zhTW"]):
                print(f"    {item['code']:6s} → {item['zhTW']}")

        if rule["unresolved_codes"]:
            print(f"  ⚠️ 未找到 zhTW 名稱的 code ({len(rule['unresolved_codes'])} 項):")
            for code in rule["unresolved_codes"]:
                print(f"    {code}")

        if not rule["specific_items_hidden"] and not rule["categories_hidden"] and not rule["itemCategory_hidden"]:
            print("  (無特定物品或類別)")


def cross_check_sell_protect(results, code_to_name, filter_data):
    """比對 filter 隱藏的 itemCode 與 sell.py 的 protect 清單"""
    # sell.py hardcoded protect lists
    SELL_PROTECT = {
        "blue": ["珠寶", "珠實", "珠賓", "咒符", "鑲孔"],
        "white": [
            "活力藥水", "全方位活力藥水", "寶石", "賓石", "無瑕",
            "巨爪", "巨鷹爪",
            "死亡面具", "莊嚴王冠", "惡魔頭骨", "骸骨面罩",
            "日冕之冠", "頭冠", "權冠",
            "阿卡拉圓盾", "阿卡拉輕圓盾", "金飾盾", "皇家盾",
            "神聖小盾", "神聖輕圓盾", "庫拉斯特盾", "薩卡蘭姆盾", "渦旋盾",
            "巨魔斧", "巨神長柄斧", "斬鐮", "絕秘斧",
            "巨型長柄斧", "巨型斬鐮",
            "水晶劍", "幻化之刃",
        ],
        "yellow": ["(整個顏色不賣)"],
        "gray": [
            "骸骨魔杖", "君主盾", "法師鎧甲", "統御者鎧甲",
            "巨爪", "巨鷹爪",
            "死亡面具", "莊嚴王冠", "惡魔頭骨", "骸骨面罩",
            "日冕之冠", "頭冠", "權冠",
            "阿卡拉圓盾", "阿卡拉輕圓盾", "金飾盾", "皇家盾",
            "神聖小盾", "神聖輕圓盾", "庫拉斯特盾", "薩卡蘭姆盾", "渦旋盾",
            "巨魔斧", "巨神長柄斧", "斬鐮", "絕秘斧",
            "巨型長柄斧", "巨型斬鐮",
            "水晶劍", "幻化之刃",
        ],
    }

    # 合併所有 protect 關鍵字（白+灰，用於反向檢查）
    all_protect_names = set()
    for color, plist in SELL_PROTECT.items():
        if color != "yellow":
            all_protect_names.update(plist)

    # 收集 filter 中被 hide 的白/灰 itemCode
    hidden_codes = set()
    hidden_categories = set()
    for rule in filter_data.get("rules", []):
        if not rule.get("enabled") or rule.get("ruleType") != "hide":
            continue
        rarities = rule.get("equipmentRarity", [])
        if any(r in rarities for r in ["normal", "lowQuality", "hiQuality"]):
            hidden_codes.update(rule.get("itemCode", []))
            hidden_codes.update(rule.get("equipmentItemCode", []))
            hidden_categories.update(rule.get("equipmentCategory", []))

    print("\n" + "=" * 60)
    print("📋 sell.py protect 清單 vs filter 比對")
    print("=" * 60)

    # ── 正向檢查：protect 裡的東西是否會出現 ──
    hidden_names = set()
    for code in hidden_codes:
        zh = code_to_name.get(code)
        if zh:
            hidden_names.add(zh)

    for color, protect_list in SELL_PROTECT.items():
        if color == "yellow":
            print(f"\n🟡 {color}: 整個顏色不賣，跳過")
            continue
        icon = "🔵" if color == "blue" else "⬜" if color == "white" else "⬛"
        print(f"\n{icon} {color} protect ({len(protect_list)} 項):")
        for pname in protect_list:
            in_hidden = pname in hidden_names
            status = "🔴 被 filter 隱藏（不會出現在地上）" if in_hidden else "✅ filter 放行（會出現）"
            print(f"  {pname:12s} {status}")

    # ── 反向檢查：filter 放行但 protect 沒覆蓋的物品 ──
    print("\n" + "=" * 60)
    print("⚠️ 反向檢查：filter 放行但 protect 未覆蓋的白/灰物品")
    print("  （這些物品會顯示在地上、被撿起來、然後可能被賣掉）")
    print("=" * 60)

    # 找出 filter 沒隱藏的 itemCode（不在 hidden_codes 且不在 hidden_categories）
    # 注意：category 隱藏比 itemCode 更廣，所以兩者都要檢查
    # 但我們無法從 CASC 知道每個 itemCode 屬於哪個 category
    # 所以這裡只列出「被 filter 用 itemCode 明確隱藏」的反面

    # 規則 4 的邏輯：隱藏 category + 隱藏特定 itemCode
    # 不在 category 裡的物品 → 只能靠 itemCode 隱藏
    # 所以反向就是：不在 hidden_categories 且不在 hidden_codes 的 = 放行

    # 從規則 4 特定列出的 itemCode 找出沒被隱藏的同類物品
    # 這需要知道每個 code 的 category，CASC 裡沒有這個 mapping
    # 所以我們用一個更實用的方法：列出 protect 清單 vs filter 隱藏的差集

    # 所有 filter 放行的物品名稱（不在 hidden 裡的）
    visible_names = set(code_to_name.values()) - hidden_names
    # 過濾掉明顯不是裝備的（quest items, 技能等）
    # 但這太複雜，改用簡單方法：只列出 protect 清單中的物品是否完整

    # 更實用的反向：規則 4 的 hidden itemCode 對應的 zhTW，
    # 看看有沒有 protect 清單「應該有但沒有」的
    rule4_hidden_names = set()
    for rule in filter_data.get("rules", []):
        if rule.get("name") == "隱藏大部分白裝與鑲材":
            for code in rule.get("equipmentItemCode", []):
                zh = code_to_name.get(code)
                if zh:
                    rule4_hidden_names.add(zh)

    # 規則 4 不隱藏的類別中，如果有物品的 code 沒在 hidden_codes 裡
    # → 這些物品可能顯示 → 需要 protect
    # 找 protect 和 hidden 的差集：protect 裡有但規則4也隱藏的 = 多餘保護（但無害）
    # hidden 裡有但 protect 沒有的 = 被隱藏所以不需要保護

    # 最關鍵的問題：有沒有「符文之語底材」類型的物品，filter 放行但 protect 漏掉？
    # 這要靠人工確認，腳本能做的是列出完整清單讓 Jones 目視檢查

    # 列出規則 4 itemCode 級別隱藏的所有物品（已 hidden）和 protect 清單的對照
    not_in_protect = rule4_hidden_names - all_protect_names
    in_protect_not_hidden = all_protect_names - rule4_hidden_names - hidden_names

    if not_in_protect:
        print(f"\n📝 規則 4 隱藏的物品中，protect 清單沒有的 ({len(not_in_protect)} 項):")
        print("  （這些被 filter 隱藏了所以沒差，但如果未來你放行它們，記得加 protect）")
        for name in sorted(not_in_protect):
            print(f"    {name}")

    if in_protect_not_hidden:
        print(f"\n📝 protect 清單有但規則 4 沒特別隱藏的 ({len(in_protect_not_hidden)} 項):")
        print("  （可能靠 category 隱藏，或本來就是 filter 放行的重要物品）")
        for name in sorted(in_protect_not_hidden):
            print(f"    {name}")

    print("\n💡 如果你在遊戲中調整 filter 放行了新的白/灰物品，")
    print("   記得把它們加到 sell.py 的 protect 清單！")


def main():
    filter_data = load_json(FILTER_PATH)
    casc_items = load_json(CASC_PATH)

    code_to_name = build_code_to_name(casc_items)
    print(f"📦 CASC mapping: {len(code_to_name)} 個 itemCode → zhTW")

    results = analyze_filter(filter_data, code_to_name)
    print_analysis(results)
    cross_check_sell_protect(results, code_to_name, filter_data)

    # 儲存分析結果
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📄 分析結果已儲存: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
