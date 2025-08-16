# Weather ETL Connector

**Student**: Rithick R Rahul  
**Roll Number**: 3122225001107  

## What it does

This is a simple ETL pipeline that fetches weather data from OpenWeatherMap API and stores it in MongoDB. It gets current weather for 10 Indian cities and transforms the data before saving.

## Setup

1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get API key and setup environment**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api) for a free API key
   - Create a `.env` file with:
   ```
   API_KEY=your_api_key_here
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=etl_database
   COLLECTION_NAME=openweather_data_raw
   ```

3. **Start MongoDB**
   ```bash
   mongod
   ```

4. **Run the script**
   ```bash
   python etl_connector.py
   ```

## What happens

1. **Extract**: Calls OpenWeatherMap API for 10 cities
2. **Transform**: Cleans and organizes the weather data  
3. **Load**: Saves to MongoDB collection `openweather_data_raw`

## Cities covered
Chennai, Mumbai, Delhi, Bangalore, Hyderabad, Kolkata, Coimbatore, Madurai, Pune, Ahmedabad

## Output
The script shows a summary with total records and data quality scores when it finishes.
![alt text](<Screenshot 2025-08-14 at 00.59.08.png>)

## Troubleshooting

- **MongoDB connection error**: Make sure MongoDB is running
- **API rate limit**: Script handles this automatically with delays
- **SSL errors**: Usually environment related, the core functionality still works

## Files
- `etl_connector.py` - Main ETL script
- `requirements.txt` - Dependencies  
- `.env` - Configuration (API keys, DB settings)
- `etl_connector.log` - Log file with run details
