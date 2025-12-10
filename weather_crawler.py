import requests
import json
import sqlite3
from pathlib import Path
from datetime import datetime


# CWA API 配置
API_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-A0010-001"
API_KEY = "CWA-E194E281-FBA1-4A1F-8F4D-1422CA148CCB"


def fetch_weather_data():
    """從 CWA API 爬取農業氣象預報數據"""
    print("📡 開始爬取 CWA 農業氣象預報數據...")
    
    try:
        params = {
            'Authorization': API_KEY,
            'format': 'JSON'
        }
        
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("✅ 數據爬取成功")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 請求失敗: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失敗: {str(e)}")
        return None


def parse_weather_data(data):
    """解析 API 返回的 JSON 數據"""
    print("🔍 開始解析數據...")
    
    weather_data = []
    
    try:
        # 導航到天氣預報數據
        locations = data['records']['Locations'][0]['Location']
        
        for location in locations:
            location_name = location['LocationName']
            weather_elements = location['WeatherElements']
            
            # 提取各氣象要素的每日數據
            wx_daily = weather_elements['Wx']
            maxt_daily = weather_elements['MaxT']
            mint_daily = weather_elements['MinT']
            
            # 按日期組合數據
            for wx_entry, maxt_entry, mint_entry in zip(wx_daily, maxt_daily, mint_daily):
                data_date = wx_entry['Date']
                weather_description = wx_entry['WeatherDescription']
                max_temp = float(maxt_entry['MaxTemperature'])
                min_temp = float(mint_entry['MinTemperature'])
                
                weather_data.append({
                    'date': data_date,
                    'location': location_name,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'description': weather_description
                })
        
        print(f"✅ 成功解析 {len(weather_data)} 筆數據")
        return weather_data
        
    except KeyError as e:
        print(f"❌ 數據結構解析失敗: {str(e)}")
        return None


def save_to_database(weather_data):
    """將數據保存到 SQLite 資料庫"""
    print("💾 開始保存數據到資料庫...")
    
    try:
        db_file = Path(__file__).parent / "data.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 刪除現有的表 (用於重新運行時清理)
        cursor.execute("DROP TABLE IF EXISTS weather")
        
        # 創建新的表
        cursor.execute("""
            CREATE TABLE weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                min_temp REAL NOT NULL,
                max_temp REAL NOT NULL,
                description TEXT NOT NULL,
                fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入數據
        for data in weather_data:
            cursor.execute("""
                INSERT INTO weather (date, location, min_temp, max_temp, description)
                VALUES (?, ?, ?, ?, ?)
            """, (data['date'], data['location'], data['min_temp'], data['max_temp'], data['description']))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 成功保存 {len(weather_data)} 筆數據到資料庫")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 資料庫操作失敗: {str(e)}")
        return False


def save_to_json(weather_data, filename="weather_data.json"):
    """將數據保存為 JSON 檔案 (備份)"""
    print(f"💾 開始保存數據到 {filename}...")
    
    try:
        json_file = Path(__file__).parent / filename
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功保存 JSON 檔案: {filename}")
        return True
        
    except IOError as e:
        print(f"❌ 檔案保存失敗: {str(e)}")
        return False


def display_summary(weather_data):
    """顯示數據摘要"""
    if not weather_data:
        return
    
    import pandas as pd
    
    df = pd.DataFrame(weather_data)
    
    print("\n" + "="*80)
    print("📊 數據摘要")
    print("="*80)
    print(f"總筆數: {len(df)}")
    print(f"地點數: {df['location'].nunique()}")
    print(f"日期範圍: {df['date'].min()} 至 {df['date'].max()}")
    print(f"平均最高溫: {df['max_temp'].mean():.1f}°C")
    print(f"平均最低溫: {df['min_temp'].mean():.1f}°C")
    print("="*80 + "\n")


def main():
    """主函數 - 協調整個爬蟲流程"""
    print("\n🌤️  CWA 農業氣象預報數據爬蟲")
    print("="*80 + "\n")
    
    # 1. 爬取數據
    api_data = fetch_weather_data()
    if not api_data:
        return
    
    # 2. 解析數據
    weather_data = parse_weather_data(api_data)
    if not weather_data:
        return
    
    # 3. 保存到資料庫
    if not save_to_database(weather_data):
        return
    
    # 4. 保存到 JSON 備份
    save_to_json(weather_data)
    
    # 5. 顯示摘要
    display_summary(weather_data)
    
    print("✅ 爬蟲流程完成！")


if __name__ == "__main__":
    main()
