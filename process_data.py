import json
import sqlite3
from pathlib import Path


def main():
    # 1. Read the JSON file
    json_file = Path(__file__).parent / "F-A0010-001.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Parse the JSON data
    weather_data = []
    
    # Navigate to the weather forecasts data
    locations = data['cwaopendata']['resources']['resource']['data']['agrWeatherForecasts']['weatherForecasts']['location']
    
    for location in locations:
        location_name = location['locationName']
        weather_elements = location['weatherElements']
        
        # Get the weather (Wx), max temperature (MaxT), and min temperature (MinT) data
        wx_daily = weather_elements['Wx']['daily']
        maxt_daily = weather_elements['MaxT']['daily']
        mint_daily = weather_elements['MinT']['daily']
        
        # Combine the data by date
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
    
    # 3. Create SQLite database and table
    db_file = Path(__file__).parent / "data.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Drop the table if it exists (for clean re-runs)
    cursor.execute("DROP TABLE IF EXISTS weather")
    
    # Create the weather table
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
    
    # 4. Insert the parsed data into the database
    for item in weather_data:
        cursor.execute("""
            INSERT INTO weather (date, location, min_temp, max_temp, description)
            VALUES (?, ?, ?, ?, ?)
        """, (item['date'], item['location'], item['min_temp'], item['max_temp'], item['description']))
    
    conn.commit()
    
    # Display summary
    cursor.execute("SELECT COUNT(*) FROM weather")
    count = cursor.fetchone()[0]
    print(f"Successfully inserted {count} records into the weather table.")
    
    # Display first few records
    cursor.execute("SELECT * FROM weather LIMIT 5")
    records = cursor.fetchall()
    print("\nFirst 5 records:")
    print("ID | Date | Location | Min Temp | Max Temp | Description")
    print("-" * 80)
    for record in records:
        print(f"{record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]}")
    
    conn.close()
    print(f"\nDatabase 'data.db' created successfully at: {db_file}")


if __name__ == "__main__":
    main()
