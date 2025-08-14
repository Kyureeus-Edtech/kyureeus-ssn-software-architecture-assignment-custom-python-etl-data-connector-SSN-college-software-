This project implements a Python ETL (Extract, Transform, Load) connector that fetches current weather data from the OpenWeather API, transforms it to include only relevant fields (city, temperature, humidity, weather description, timestamp), and loads it into a MongoDB collection with an ingestion timestamp. The project uses a .env file to securely store the API key and MongoDB URI.

Setup Instructions:

Start MongoDB: Ensure MongoDB is running before executing the ETL script. You can start it either as a Windows service (Get-Service | findstr Mongo to check and net start MongoDB to start) or manually using mongod --dbpath "C:\data\db". Wait until the server displays Waiting for connections on port 27017.

Set up .env: In your project folder, create a .env file containing:
API_KEY=ada899f744a043c315e08ec7b6f1a798
MONGO_URI=mongodb://localhost:27017

Install Python Dependencies:
pip install -r requirements.txt

Run the ETL Script:
python etl_connector.py

Verify Data in MongoDB:
mongosh
use weather_db
show collections
db.weather_data.find().pretty()
