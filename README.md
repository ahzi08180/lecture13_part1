# 農業氣象預報數據分析應用

這是一個用來展示台灣農業氣象預報數據的 Streamlit 應用程式。

## 功能

- 從 JSON 檔案讀取農業氣象預報數據
- 將數據存儲到 SQLite 資料庫
- 使用 Streamlit 網頁界面展示數據
- 提供各地區溫度統計分析

## 檔案說明

- `process_data.py` - 數據處理腳本，從 JSON 檔案讀取數據並存入 SQLite 資料庫
- `app.py` - Streamlit 應用程式主文件，用於展示天氣數據
- `F-A0010-001.json` - 中央氣象署提供的農業氣象預報 JSON 數據
- `data.db` - SQLite 資料庫檔案，包含 weather 資料表

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方式

### 本地運行

1. 首先運行數據處理腳本：
```bash
python process_data.py
```

2. 然後啟動 Streamlit 應用：
```bash
streamlit run app.py
```

應用程式會在 `http://localhost:8501` 開啟。

### 線上部署 (Streamlit Cloud)

1. 將專案推送到 GitHub
2. 前往 [Streamlit Cloud](https://streamlit.io/cloud)
3. 登入並連接您的 GitHub 帳號
4. 點擊「New app」
5. 選擇您的 repository、branch 和 app file (`app.py`)
6. 點擊「Deploy」

## 資料表結構

`weather` 資料表包含以下欄位：

| 欄位名稱 | 資料型態 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵，自動遞增 |
| date | TEXT | 日期 (YYYY-MM-DD) |
| location | TEXT | 地點名稱 |
| min_temp | REAL | 最低溫度 (°C) |
| max_temp | REAL | 最高溫度 (°C) |
| description | TEXT | 天氣描述 |

## 數據來源

數據來自中央氣象署 (CWA) 提供的一週農業氣象預報 API：
- 資料集 ID: F-A0010-001
- 資源名稱: 中央氣象署氣候服務_農業氣象一週預報

## 許可證

MIT License

## 聯絡方式

如有任何問題，歡迎提出 Issue 或 Pull Request。
