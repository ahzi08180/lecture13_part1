import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path


def get_weather_data():
    """Connect to database and retrieve weather data"""
    db_file = Path(__file__).parent / "data.db"
    
    if not db_file.exists():
        st.error("❌ 錯誤：找不到 data.db 檔案")
        st.info("請先執行 process_data.py 來生成數據庫")
        return None
    
    try:
        conn = sqlite3.connect(db_file)
        query = "SELECT id, date, location, min_temp, max_temp, description FROM weather"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 連接數據庫失敗: {str(e)}")
        return None


def display_summary_statistics(df):
    """Display summary statistics"""
    st.subheader("🌤️  農業氣象預報數據統計")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總筆數", len(df))
    with col2:
        st.metric("地點數", df['location'].nunique())
    with col3:
        st.metric("日期範圍", f"{df['date'].min()} 至 {df['date'].max()}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("平均最高溫", f"{df['max_temp'].mean():.1f}°C")
    with col2:
        st.metric("平均最低溫", f"{df['min_temp'].mean():.1f}°C")


def display_weather_data(df):
    """Display all weather data in table format"""
    st.subheader("詳細天氣數據")
    
    # Rename columns to Chinese for display
    df_display = df.rename(columns={
        'id': '序號',
        'date': '日期',
        'location': '地點',
        'min_temp': '最低溫',
        'max_temp': '最高溫',
        'description': '天氣描述'
    })
    
    st.dataframe(df_display, use_container_width=True)


def display_location_statistics(df):
    """Display statistics by location"""
    st.subheader("各地區溫度統計")
    
    location_stats = df.groupby('location').agg({
        'min_temp': ['min', 'mean', 'max'],
        'max_temp': ['min', 'mean', 'max']
    }).round(1)
    
    # Flatten column names
    location_stats.columns = ['最低溫_最小', '最低溫_平均', '最低溫_最大', 
                              '最高溫_最小', '最高溫_平均', '最高溫_最大']
    
    st.dataframe(location_stats, use_container_width=True)


def main():
    """Main function"""
    st.set_page_config(page_title="農業氣象預報數據分析", page_icon="🌤️", layout="wide")
    
    st.title("🌤️  農業氣象預報數據分析應用")
    
    # Get data from database
    df = get_weather_data()
    
    if df is None or df.empty:
        st.error("❌ 無法獲取數據")
        return
    
    # Display statistics
    display_summary_statistics(df)
    
    st.divider()
    
    # Display all data
    display_weather_data(df)
    
    st.divider()
    
    # Display location statistics
    display_location_statistics(df)
    
    st.success("✅ 數據顯示完成")


if __name__ == "__main__":
    main()

