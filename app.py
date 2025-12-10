import streamlit as st
import sqlite3
import pandas as pd
import json
from pathlib import Path


def initialize_database():
    """Initialize database if it doesn't exist"""
    db_file = Path(__file__).parent / "data.db"
    
    # Check if database exists and has data
    if db_file.exists():
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM weather")
            count = cursor.fetchone()[0]
            conn.close()
            if count > 0:
                return  # Database already populated
        except:
            pass
    
    # Initialize database from JSON
    json_file = Path(__file__).parent / "F-A0010-001.json"
    
    if not json_file.exists():
        st.error("❌ 錯誤：找不到 F-A0010-001.json 檔案")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        weather_data = []
        locations = data['cwaopendata']['resources']['resource']['data']['agrWeatherForecasts']['weatherForecasts']['location']
        
        for location in locations:
            location_name = location['locationName']
            weather_elements = location['weatherElements']
            
            wx_daily = weather_elements['Wx']['daily']
            maxt_daily = weather_elements['MaxT']['daily']
            mint_daily = weather_elements['MinT']['daily']
            
            for wx_entry, maxt_entry, mint_entry in zip(wx_daily, maxt_daily, mint_daily):
                data_date = wx_entry['dataDate']
                weather_description = wx_entry['weather']
                max_temp = float(maxt_entry['temperature'])
                min_temp = float(mint_entry['temperature'])
                
                weather_data.append({
                    'date': data_date,
                    'location': location_name,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'description': weather_description
                })
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS weather")
        cursor.execute("""
            CREATE TABLE weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                min_temp REAL NOT NULL,
                max_temp REAL NOT NULL,
                description TEXT NOT NULL
            )
        """)
        
        for item in weather_data:
            cursor.execute("""
                INSERT INTO weather (date, location, min_temp, max_temp, description)
                VALUES (?, ?, ?, ?, ?)
            """, (item['date'], item['location'], item['min_temp'], item['max_temp'], item['description']))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"❌ 數據初始化失敗: {str(e)}")


def get_weather_data():
    """Connect to database and retrieve weather data"""
    db_file = Path(__file__).parent / "data.db"
    conn = sqlite3.connect(db_file)
    query = "SELECT id, date, location, min_temp, max_temp, description FROM weather"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def main():
    st.set_page_config(page_title="農業氣象預報", layout="wide")
    
    st.title("🌤️ 農業氣象預報數據")
    st.markdown("---")
    
    # Initialize database if needed
    initialize_database()
    
    # Get data from database
    df = get_weather_data()
    
    # Rename columns to Chinese
    df_display = df.rename(columns={
        'id': '序號',
        'date': '日期',
        'location': '地點',
        'min_temp': '最低溫 (°C)',
        'max_temp': '最高溫 (°C)',
        'description': '天氣描述'
    })
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總筆數", len(df_display))
    
    with col2:
        st.metric("地點數", df_display['地點'].nunique())
    
    with col3:
        st.metric("日期範圍", f"{df_display['日期'].min()} 至 {df_display['日期'].max()}")
    
    with col4:
        st.metric("平均最高溫", f"{df_display['最高溫 (°C)'].mean():.1f}°C")
    
    st.markdown("---")
    
    # Display dataframe
    st.subheader("詳細天氣數據")
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Additional statistics
    st.subheader("各地區統計")
    location_stats = df_display.groupby('地點').agg({
        '最低溫 (°C)': ['min', 'mean', 'max'],
        '最高溫 (°C)': ['min', 'mean', 'max']
    }).round(1)
    
    st.dataframe(location_stats, use_container_width=True)


if __name__ == "__main__":
    main()
