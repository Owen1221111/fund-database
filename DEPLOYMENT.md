# 🚀 部署指南

## 步驟 1：在 GitHub 建立 Repository

1. 前往 GitHub: https://github.com/new
2. Repository name: `fund-database`
3. Description: `台灣基金資料庫 - 提供境外基金與期信基金的完整資料`
4. 選擇 **Public** (讓 GitHub Pages 可以免費使用)
5. **不要** 勾選 "Add a README file" (我們已經有了)
6. 點擊 **Create repository**

---

## 步驟 2：上傳專案到 GitHub

在終端機中執行（在 fund-database 資料夾內）：

```bash
cd /Users/chehungliu/Desktop/fund-database

# 初始化 Git
git init

# 設定你的 Git 資訊（如果還沒設定）
git config user.name "Owen1221111"
git config user.email "your-email@example.com"

# 加入所有檔案
git add .

# 第一次提交
git commit -m "🎉 Initial commit: 台灣基金資料庫"

# 設定主分支名稱為 main
git branch -M main

# 連接到 GitHub 遠端 repo
git remote add origin https://github.com/Owen1221111/fund-database.git

# 推送到 GitHub
git push -u origin main
```

---

## 步驟 3：啟用 GitHub Pages

1. 在 GitHub 專案頁面，點擊 **Settings**
2. 左側選單點擊 **Pages**
3. **Source** 選擇：
   - Branch: `main`
   - Folder: `/ (root)`
4. 點擊 **Save**
5. 等待 1-2 分鐘，你的網站就會上線！

網址將會是：
```
https://owen1221111.github.io/fund-database/
```

---

## 步驟 4：啟用 GitHub Actions

GitHub Actions 會自動啟用，無需額外設定。

### 確認 Actions 正常運作：

1. 點擊專案的 **Actions** 頁籤
2. 你應該會看到 "更新基金淨值" workflow
3. 可以點擊 **Run workflow** 手動測試一次

### 自動更新時間：

- 每天早上 9:00 (台灣時間)
- 也可以手動觸發更新

---

## 步驟 5：測試 API

等待 GitHub Pages 部署完成後（約 1-2 分鐘），測試 API：

### 在瀏覽器開啟：
```
https://owen1221111.github.io/fund-database/
```

### 測試 API 端點：
```
https://owen1221111.github.io/fund-database/data/funds-popular.json
https://owen1221111.github.io/fund-database/data/funds-nav-latest.json
https://owen1221111.github.io/fund-database/data/last-update.json
```

---

## 📱 在你的 APP 中使用

### 修改 FundMasterService.swift

原本的模擬資料改成從 GitHub Pages 載入：

```swift
// FundMasterService.swift

private func fetchFundDataFromAPI() async throws -> [FundMasterData] {
    let apiURL = "https://owen1221111.github.io/fund-database/data/funds-popular.json"

    guard let url = URL(string: apiURL) else {
        throw NSError(domain: "Invalid URL", code: -1)
    }

    let (data, _) = try await URLSession.shared.data(from: url)

    // 解析 JSON
    struct Response: Codable {
        let lastUpdate: String
        let count: Int
        let funds: [FundData]
    }

    struct FundData: Codable {
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

    let response = try JSONDecoder().decode(Response.self, from: data)

    // 轉換為 FundMasterData
    return response.funds.map { fund in
        FundMasterData(
            fundCode: fund.fundCode,
            fundName: fund.fundName,
            companyName: fund.company,
            fundType: fund.type,
            fundRegion: fund.region
        )
    }
}
```

### 修改 FundNavService.swift

整合 GitHub Pages 淨值快取：

```swift
// FundNavService.swift

func getNav(for fundCode: String) async throws -> String? {
    // 1. 先從 GitHub Pages 快取查詢
    let cacheURL = "https://owen1221111.github.io/fund-database/data/funds-nav-latest.json"

    guard let url = URL(string: cacheURL) else { return nil }

    let (data, _) = try await URLSession.shared.data(from: url)

    struct NavCache: Codable {
        let lastUpdate: String
        let navData: [String: NavInfo]
    }

    struct NavInfo: Codable {
        let nav: String
        let date: String
        let fundName: String
    }

    let cache = try JSONDecoder().decode(NavCache.self, from: data)

    // 2. 用 ISIN 或基金代碼查詢
    if let navInfo = cache.navData[fundCode] {
        print("✅ 從 GitHub Pages 找到淨值：\(fundCode) = \(navInfo.nav)")
        return navInfo.nav
    }

    // 3. 如果找不到，再查 TDCC（你原本的邏輯）
    return try await fetchNavFromTDCC(fundCode: fundCode)
}
```

---

## 🔄 未來更新流程

### 本地測試：
```bash
cd /Users/chehungliu/Desktop/fund-database
python3 fetch_tdcc_data.py
```

### 推送到 GitHub：
```bash
git add data/*.json
git commit -m "📊 更新基金資料"
git push
```

### 自動更新：
- 無需手動操作
- GitHub Actions 每天自動更新
- 在 Actions 頁籤可查看執行記錄

---

## ❓ 常見問題

### Q: GitHub Pages 沒有顯示網頁？
A: 等待 1-2 分鐘讓 GitHub 部署完成。檢查 Settings > Pages 確認已啟用。

### Q: API 回傳 404？
A: 確認檔案路徑正確：`/data/funds-popular.json`

### Q: Actions 沒有自動執行？
A: 檢查 `.github/workflows/update-nav.yml` 是否正確推送到 GitHub。

### Q: 想要改變自動更新時間？
A: 編輯 `.github/workflows/update-nav.yml`，修改 `cron` 設定。

---

## 🎉 完成！

你現在有了一個：
- ✅ 完全免費的基金資料庫 API
- ✅ 每天自動更新
- ✅ 超快速讀取（JSON 直接載入）
- ✅ 不依賴 Yahoo Finance（避免風險）
- ✅ 無需維護伺服器

下一步：修改你的 APP，改用新的 API！
