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


def cross_check_sell_protect(results, code_to_name):
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

    # 收集 filter 中被 hide 的白/灰 itemCode 的 zhTW 名稱
    hidden_white_gray_names = set()
    for rule in results:
        if not rule["enabled"] or rule["ruleType"] != "hide":
            continue
        rarities = rule["rarity"]
        # 白色 = normal/lowQuality/hiQuality, 灰色 = normal with ethereal/socketed
        if any(r in rarities for r in ["normal", "lowQuality", "hiQuality"]):
            for item in rule["specific_items_hidden"]:
                hidden_white_gray_names.add(item["zhTW"])

    # 收集所有 zhTW 名稱（全物品池）
    all_names = set(code_to_name.values())

    # filter 沒隱藏的白/灰 = 會顯示在地上
    # 注意：這只是 itemCode 級別的，category 級別的隱藏更廣
    # 但 itemCode 是精確覆蓋的

    print("\n" + "=" * 60)
    print("📋 sell.py protect 清單 vs filter 比對")
    print("=" * 60)

    # 檢查 protect 清單中的物品是否在 filter 的隱藏名單中（被隱藏 = 不會出現 = 不需要保護）
    for color, protect_list in SELL_PROTECT.items():
        if color == "yellow":
            print(f"\n🟡 {color}: 整個顏色不賣，跳過")
            continue
        print(f"\n{'🔵' if color == 'blue' else '⬜' if color == 'white' else '⬛'} {color} protect ({len(protect_list)} 項):")
        for pname in protect_list:
            in_hidden = pname in hidden_white_gray_names
            status = "🔴 被 filter 隱藏（不會出現在地上）" if in_hidden else "✅ filter 放行（會出現）"
            print(f"  {pname:12s} {status}")


def main():
    filter_data = load_json(FILTER_PATH)
    casc_items = load_json(CASC_PATH)

    code_to_name = build_code_to_name(casc_items)
    print(f"📦 CASC mapping: {len(code_to_name)} 個 itemCode → zhTW")

    results = analyze_filter(filter_data, code_to_name)
    print_analysis(results)
    cross_check_sell_protect(results, code_to_name)

    # 儲存分析結果
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📄 分析結果已儲存: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
