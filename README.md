# 📊 台灣基金資料庫 (Taiwan Fund Database)

完整的台灣境外基金與期信基金資料庫，提供基金主檔和每日淨值查詢。

## 🌟 特色

- ✅ **真實資料**：整合臺灣集中保管結算所 (TDCC) 開放資料
- ✅ **每日更新**：GitHub Actions 自動更新淨值（每天早上 9 點）
- ✅ **快速查詢**：JSON 格式，直接讀取無需 API Key
- ✅ **完全免費**：GitHub Pages 託管，無流量限制
- ✅ **跨平台**：支援 iOS、Android、Web 等任何平台

---

## 📊 資料統計

- **總基金數量**：300+ 檔
- **熱門基金**：100 檔
- **資料來源**：TDCC 開放資料平台
- **更新頻率**：每日自動更新

---

## 🔌 API 端點

### 基礎 URL
```
https://owen1221111.github.io/fund-database/data/
```

### 1. 完整基金清單
```
GET /data/funds-master.json
```

**回應格式：**
```json
{
  "lastUpdate": "2025-12-09T16:51:20",
  "count": 300,
  "funds": [
    {
      "fundCode": "AA1015",
      "fundName": "安聯全球人工智慧基金",
      "isinCode": "LU1254033170",
      "company": "安聯投信",
      "type": "境外基金",
      "region": "境外",
      "currency": "USD",
      "latestNav": "25.50",
      "navDate": "2025-12-08"
    }
  ]
}
```

---

### 2. 熱門基金清單 (TOP 100)
```
GET /data/funds-popular.json
```

精選 100 檔熱門基金，適合 APP 啟動時快速載入。

---

### 3. 最新淨值快取
```
GET /data/funds-nav-latest.json
```

**回應格式：**
```json
{
  "lastUpdate": "2025-12-09T16:51:20",
  "navData": {
    "LU1254033170": {
      "nav": "25.50",
      "date": "2025-12-08",
      "fundName": "安聯全球人工智慧基金"
    }
  }
}
```

---

### 4. 最後更新時間
```
GET /data/last-update.json
```

**回應格式：**
```json
{
  "lastUpdate": "2025-12-09T16:51:20",
  "timestamp": 1733735480,
  "totalFunds": 300,
  "popularFunds": 100,
  "navCacheSize": 15
}
```

---

## 💻 使用範例

### Swift (iOS)
```swift
import Foundation

struct FundDatabase: Codable {
    let lastUpdate: String
    let count: Int
    let funds: [Fund]
}

struct Fund: Codable {
    let fundCode: String
    let fundName: String
    let isinCode: String
    let company: String
    let type: String
    let region: String
    let currency: String
    let latestNav: String
    let navDate: String
}

// 載入熱門基金
let url = URL(string: "https://owen1221111.github.io/fund-database/data/funds-popular.json")!

URLSession.shared.dataTask(with: url) { data, response, error in
    guard let data = data else { return }

    let decoder = JSONDecoder()
    if let database = try? decoder.decode(FundDatabase.self, from: data) {
        print("✅ 載入 \(database.count) 檔基金")

        for fund in database.funds {
            print("\(fund.fundName): \(fund.latestNav)")
        }
    }
}.resume()
```

---

### JavaScript (Web)
```javascript
// 載入熱門基金
fetch('https://owen1221111.github.io/fund-database/data/funds-popular.json')
  .then(response => response.json())
  .then(data => {
    console.log(`✅ 載入 ${data.count} 檔基金`);

    data.funds.forEach(fund => {
      console.log(`${fund.fundName}: ${fund.latestNav}`);
    });
  });

// 查詢特定基金淨值（使用 ISIN）
fetch('https://owen1221111.github.io/fund-database/data/funds-nav-latest.json')
  .then(response => response.json())
  .then(data => {
    const isinCode = 'LU1254033170';
    const navInfo = data.navData[isinCode];

    if (navInfo) {
      console.log(`${navInfo.fundName}: ${navInfo.nav} (${navInfo.date})`);
    }
  });
```

---

### Python
```python
import requests

# 載入熱門基金
response = requests.get('https://owen1221111.github.io/fund-database/data/funds-popular.json')
data = response.json()

print(f"✅ 載入 {data['count']} 檔基金")

for fund in data['funds']:
    print(f"{fund['fundName']}: {fund['latestNav']}")
```

---

## 🛠️ 本地開發

### 1. Clone 專案
```bash
git clone https://github.com/Owen1221111/fund-database.git
cd fund-database
```

### 2. 抓取最新資料
```bash
python3 fetch_tdcc_data.py
```

### 3. 開啟本地伺服器
```bash
python3 -m http.server 8000
```

瀏覽器開啟：`http://localhost:8000`

---

## 📅 自動更新

此專案使用 GitHub Actions 每天自動更新基金淨值：

- **更新時間**：每天早上 9:00 (台灣時間)
- **更新內容**：基金淨值、熱門基金清單、淨值快取
- **Workflow 檔案**：`.github/workflows/update-nav.yml`

### 手動觸發更新
在 GitHub 專案頁面：
1. 點擊 **Actions** 頁籤
2. 選擇 **更新基金淨值** workflow
3. 點擊 **Run workflow**

---

## 📁 專案結構

```
fund-database/
├── data/                           # 資料目錄
│   ├── funds-master.json          # 完整基金清單
│   ├── funds-popular.json         # 熱門基金 TOP 100
│   ├── funds-nav-latest.json      # 最新淨值快取
│   └── last-update.json           # 最後更新時間
├── .github/
│   └── workflows/
│       └── update-nav.yml         # GitHub Actions 自動更新
├── index.html                     # 資料庫首頁
├── fetch_tdcc_data.py            # 資料抓取腳本
└── README.md                      # 說明文件
```

---

## 🔗 資料來源

- **臺灣集中保管結算所 (TDCC)**
  - 境外基金淨值：https://opendata.tdcc.com.tw/getOD.ashx?id=3-4
  - 期信基金淨值：https://opendata.tdcc.com.tw/getOD.ashx?id=5-4

---

## 📝 授權

本專案採用 MIT 授權。

資料來源為臺灣集中保管結算所開放資料，請遵守相關使用規範。

---

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

---

## 📧 聯絡方式

如有問題或建議，請透過 GitHub Issues 聯繫。

---

**Made with ❤️ by Owen1221111**
