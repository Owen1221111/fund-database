#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDCC 基金資料抓取腳本
從臺灣集中保管結算所抓取基金主檔和淨值資料
使用 Python 標準庫（無需額外安裝套件）
"""

import urllib.request
import csv
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import io

# 設定台灣時區 (UTC+8)
TW_TZ = timezone(timedelta(hours=8))

# API 端點
OFFSHORE_NAV_API = "https://opendata.tdcc.com.tw/getOD.ashx?id=3-4"  # 境外基金淨值
FUTURES_NAV_API = "https://opendata.tdcc.com.tw/getOD.ashx?id=5-4"   # 期信基金淨值
DOMESTIC_NAV_API = "https://www.sitca.org.tw/MemberK0000/F/03/nav.csv"  # 境內基金淨值

def fetch_tdcc_csv(api_url: str) -> List[Dict]:
    """
    從 TDCC API 抓取 CSV 資料並解析
    """
    print(f"正在抓取資料：{api_url}")

    try:
        # 使用 urllib 抓取資料
        with urllib.request.urlopen(api_url, timeout=30) as response:
            csv_text = response.read().decode('utf-8-sig')  # 使用 utf-8-sig 自動去除 BOM

        # 解析 CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))

        data = []
        for row in csv_reader:
            data.append(row)

        print(f"✅ 成功抓取 {len(data)} 筆資料")
        return data

    except Exception as e:
        print(f"❌ 抓取失敗：{e}")
        return []

def process_fund_data(offshore_data: List[Dict], futures_data: List[Dict], domestic_data: List[Dict]) -> Dict:
    """
    處理並合併基金資料
    注意：TDCC API 回傳同一基金的多筆歷史資料，需要依基金代碼分組並取最新日期
    """
    all_funds = []
    nav_cache = {}

    # === 處理境內基金 ===
    domestic_grouped = {}
    for fund in domestic_data:
        # 使用基金統編作為唯一識別碼
        fund_id = fund.get('基金統編', '').strip()
        fund_code = fund.get('基金代號', '').strip()
        date = fund.get('日期', '').strip()

        if not fund_id:
            continue

        # 保留最新日期的資料
        if fund_id not in domestic_grouped or date > domestic_grouped[fund_id].get('日期', ''):
            domestic_grouped[fund_id] = fund

    # 處理分組後的境內基金
    for fund in domestic_grouped.values():
        fund_id = fund.get('基金統編', '').strip()
        fund_code = fund.get('基金代號', '').strip()
        fund_name = fund.get('基金名稱', '').strip()
        nav = fund.get('基金淨值', '').strip()
        date = fund.get('日期', '').strip()
        currency = fund.get('幣別', '').strip()
        company = fund.get('公司名稱', '').strip()
        isin_code = fund.get('受益憑證代號', '').strip()

        if fund_id and fund_name:
            fund_info = {
                "fundCode": fund_code if fund_code else fund_id,
                "fundName": fund_name,
                "isinCode": isin_code if isin_code else fund_id,
                "company": company,
                "type": "境內基金",
                "region": "境內",
                "currency": currency or "TWD",
                "latestNav": nav,
                "navDate": date
            }
            all_funds.append(fund_info)

            # 建立淨值快取
            if fund_code and nav:
                nav_cache[fund_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }
            if isin_code and nav:
                nav_cache[isin_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }
            if fund_id and nav:
                nav_cache[fund_id] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }

    # 先依 ISIN 分組並取最新資料（ISIN 是唯一的基金識別碼）
    offshore_grouped = {}
    for fund in offshore_data:
        isin_code = fund.get('ISINCODE', '').strip()
        date = fund.get('日期', '').strip()

        if not isin_code:
            continue

        # 如果這個 ISIN 還沒有記錄，或是日期更新，則更新
        if isin_code not in offshore_grouped or date > offshore_grouped[isin_code].get('日期', ''):
            offshore_grouped[isin_code] = fund

    # 處理境外基金（使用分組後的最新資料）
    for fund in offshore_grouped.values():
        fund_code = fund.get('基金代碼', '').strip()
        fund_name = fund.get('基金名稱', '').strip()
        isin_code = fund.get('ISINCODE', '').strip()  # 修正欄位名稱
        nav = fund.get('基金淨值(金額)', '').strip()    # 修正欄位名稱
        date = fund.get('日期', '').strip()            # 修正欄位名稱
        currency = fund.get('計價幣別', '').strip()
        institution = fund.get('境外基金機構', '').strip()

        if isin_code and fund_name:  # 改用 ISIN 判斷（ISIN 才是唯一識別碼）
            fund_info = {
                "fundCode": fund_code if fund_code else isin_code,  # 如果沒有基金代碼就用 ISIN
                "fundName": fund_name,
                "isinCode": isin_code,
                "company": institution,
                "type": "境外基金",
                "region": "境外",
                "currency": currency or "USD",
                "latestNav": nav,
                "navDate": date
            }
            all_funds.append(fund_info)

            # 建立淨值快取（使用 ISIN 和基金代碼）
            if isin_code and nav:
                nav_cache[isin_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }
            if fund_code and nav:
                nav_cache[fund_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }

    # 處理期信基金（同樣需要分組）
    futures_grouped = {}
    for fund in futures_data:
        fund_code = fund.get('基金代碼', '').strip()
        date = fund.get('淨值日期', '').strip()

        if not fund_code:
            continue

        if fund_code not in futures_grouped or date > futures_grouped[fund_code].get('淨值日期', ''):
            futures_grouped[fund_code] = fund

    for fund in futures_grouped.values():
        fund_code = fund.get('基金代碼', '').strip()
        fund_name = fund.get('基金名稱', '').strip()
        isin_code = fund.get('ISIN', '').strip()
        nav = fund.get('淨值', '').strip()
        date = fund.get('淨值日期', '').strip()
        currency = fund.get('計價幣別', '').strip()
        institution = fund.get('期信機構', '').strip()

        if fund_code and fund_name:
            fund_info = {
                "fundCode": fund_code,
                "fundName": fund_name,
                "isinCode": isin_code,
                "company": institution,
                "type": "期信基金",
                "region": "境外",
                "currency": currency or "USD",
                "latestNav": nav,
                "navDate": date
            }
            all_funds.append(fund_info)

            # 建立淨值快取
            if isin_code and nav:
                nav_cache[isin_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }
            if fund_code and nav:
                nav_cache[fund_code] = {
                    "nav": nav,
                    "date": date,
                    "fundName": fund_name
                }

    return {
        "funds": all_funds,
        "navCache": nav_cache
    }

def select_popular_funds(all_funds: List[Dict], limit: int = 100) -> List[Dict]:
    """
    選出熱門基金 TOP N
    優先選擇常見投信公司的基金
    """
    # 優先選擇常見投信公司的基金（境內+境外）
    priority_companies = [
        # 境內投信
        "元大", "富邦", "國泰", "群益", "統一",
        "復華", "日盛", "野村", "兆豐", "台新",
        "中國信託", "凱基", "永豐", "第一金", "合庫",
        # 境外投信
        "富蘭克林", "聯博", "貝萊德", "施羅德", "摩根",
        "安聯", "柏瑞", "安本標準", "PIMCO", "駿利亨德森",
        "景順", "霸菱", "法巴", "駿利", "瀚亞"
    ]

    popular = []

    # 先加入優先公司的基金
    for company in priority_companies:
        matching_funds = [f for f in all_funds if company in f.get("company", "") or company in f.get("fundName", "")]
        popular.extend(matching_funds[:5])  # 每家最多取 5 檔
        if len(popular) >= limit:
            break

    # 如果不足，補充其他基金
    if len(popular) < limit:
        remaining = [f for f in all_funds if f not in popular]
        popular.extend(remaining[:limit - len(popular)])

    return popular[:limit]

def save_json(data: Dict, filename: str):
    """
    儲存 JSON 檔案
    """
    filepath = f"data/{filename}"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已儲存：{filepath}")
    except Exception as e:
        print(f"❌ 儲存失敗：{e}")

def main():
    print("=" * 60)
    print("🚀 TDCC 基金資料抓取開始")
    print("=" * 60)

    # 1. 抓取資料
    print("\n📥 步驟 1：抓取基金資料")
    domestic_data = fetch_tdcc_csv(DOMESTIC_NAV_API)
    offshore_data = fetch_tdcc_csv(OFFSHORE_NAV_API)
    futures_data = fetch_tdcc_csv(FUTURES_NAV_API)

    if not domestic_data and not offshore_data and not futures_data:
        print("❌ 無法抓取任何資料，終止程序")
        return

    # 2. 處理資料
    print("\n⚙️  步驟 2：處理基金資料")
    processed = process_fund_data(offshore_data, futures_data, domestic_data)
    all_funds = processed["funds"]
    nav_cache = processed["navCache"]

    print(f"✅ 共處理 {len(all_funds)} 檔基金")
    print(f"✅ 建立 {len(nav_cache)} 筆淨值快取")

    # 3. 選出熱門基金
    print("\n🌟 步驟 3：選出熱門基金 TOP 100")
    popular_funds = select_popular_funds(all_funds, limit=100)
    print(f"✅ 已選出 {len(popular_funds)} 檔熱門基金")

    # 4. 儲存 JSON 檔案
    print("\n💾 步驟 4：儲存 JSON 檔案")

    # 4.1 完整基金清單
    funds_master = {
        "lastUpdate": datetime.now(TW_TZ).isoformat(),
        "count": len(all_funds),
        "funds": all_funds
    }
    save_json(funds_master, "funds-master.json")

    # 4.2 熱門基金清單
    funds_popular = {
        "lastUpdate": datetime.now(TW_TZ).isoformat(),
        "count": len(popular_funds),
        "funds": popular_funds
    }
    save_json(funds_popular, "funds-popular.json")

    # 4.3 淨值快取
    funds_nav = {
        "lastUpdate": datetime.now(TW_TZ).isoformat(),
        "navData": nav_cache
    }
    save_json(funds_nav, "funds-nav-latest.json")

    # 4.4 最後更新時間
    last_update = {
        "lastUpdate": datetime.now(TW_TZ).isoformat(),
        "timestamp": int(datetime.now(TW_TZ).timestamp()),
        "totalFunds": len(all_funds),
        "popularFunds": len(popular_funds),
        "navCacheSize": len(nav_cache)
    }
    save_json(last_update, "last-update.json")

    # 5. 統計資訊
    print("\n" + "=" * 60)
    print("📊 統計資訊")
    print("=" * 60)
    print(f"總基金數量：{len(all_funds)} 檔")
    print(f"熱門基金數量：{len(popular_funds)} 檔")
    print(f"淨值快取數量：{len(nav_cache)} 筆")
    print(f"最後更新時間：{datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("✅ 所有資料已成功產生！")
    print("=" * 60)

if __name__ == "__main__":
    main()
