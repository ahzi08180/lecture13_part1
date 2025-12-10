import sqlite3
import pandas as pd
from pathlib import Path


def get_weather_data():
    """Connect to database and retrieve weather data"""
    db_file = Path(__file__).parent / "data.db"
    
    if not db_file.exists():
        print("❌ 錯誤：找不到 data.db 檔案")
        print("請先執行 process_data.py 來生成數據庫")
        return None
    
    try:
        conn = sqlite3.connect(db_file)
        query = "SELECT id, date, location, min_temp, max_temp, description FROM weather"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ 連接數據庫失敗: {str(e)}")
        return None


def display_summary_statistics(df):
    """Display summary statistics"""
    print("\n" + "="*80)
    print("🌤️  農業氣象預報數據統計")
    print("="*80)
    print(f"總筆數: {len(df)}")
    print(f"地點數: {df['location'].nunique()}")
    print(f"日期範圍: {df['date'].min()} 至 {df['date'].max()}")
    print(f"平均最高溫: {df['max_temp'].mean():.1f}°C")
    print(f"平均最低溫: {df['min_temp'].mean():.1f}°C")
    print("="*80 + "\n")


def display_weather_data(df):
    """Display all weather data in table format"""
    print("\n詳細天氣數據")
    print("-"*120)
    
    # Rename columns to Chinese for display
    df_display = df.rename(columns={
        'id': '序號',
        'date': '日期',
        'location': '地點',
        'min_temp': '最低溫',
        'max_temp': '最高溫',
        'description': '天氣描述'
    })
    
    print(df_display.to_string(index=False))
    print("-"*120 + "\n")


def display_location_statistics(df):
    """Display statistics by location"""
    print("\n各地區溫度統計")
    print("-"*100)
    
    location_stats = df.groupby('location').agg({
        'min_temp': ['min', 'mean', 'max'],
        'max_temp': ['min', 'mean', 'max']
    }).round(1)
    
    # Flatten column names
    location_stats.columns = ['最低溫_最小', '最低溫_平均', '最低溫_最大', 
                              '最高溫_最小', '最高溫_平均', '最高溫_最大']
    
    print(location_stats.to_string())
    print("-"*100 + "\n")


def main():
    """Main function"""
    print("\n🌤️  農業氣象預報數據分析應用")
    print("="*80)
    
    # Get data from database
    df = get_weather_data()
    
    if df is None or df.empty:
        print("❌ 無法獲取數據")
        return
    
    # Display statistics
    display_summary_statistics(df)
    
    # Display all data
    display_weather_data(df)
    
    # Display location statistics
    display_location_statistics(df)
    
    print("✅ 數據顯示完成")


if __name__ == "__main__":
    main()

