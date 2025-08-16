"""
Custom Python ETL Data Connector
Student: Rithick R Rahul - 3122225001107
API Provider: OpenWeatherMap API
Description: ETL pipeline to extract weather data from OpenWeatherMap API,
transform it for MongoDB compatibility, and load into MongoDB collection.
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_connector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLDataConnector:
    """Custom ETL Data Connector for API data extraction and MongoDB loading"""

    def __init__(self):
        # API Configuration
        self.base_url = os.getenv('API_BASE_URL', 'https://api.openweathermap.org/data/2.5')
        self.api_key = os.getenv('API_KEY', '')
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1'))  # seconds

        # MongoDB Configuration
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('DB_NAME', 'etl_database')
        self.collection_name = os.getenv('COLLECTION_NAME', 'openweather_data_raw')

        # Initialize MongoDB connection
        self.mongo_client = None
        self.db = None
        self.collection = None

        # Request session for connection pooling
        self.session = requests.Session()

        # Cities to get weather data for
        self.cities = os.getenv('CITIES', 'Chennai,Mumbai,Delhi,Bangalore,Hyderabad,Kolkata').split(',')

    def connect_to_mongodb(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            self.mongo_client = MongoClient(self.mongo_uri)
            # Test connection
            self.mongo_client.admin.command('ismaster')
            self.db = self.mongo_client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Connected to MongoDB: {self.db_name}.{self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            return False

    def extract_data(self, endpoint: str = '/weather', params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Extract weather data from OpenWeatherMap API for multiple cities
        
        Args:
            endpoint: API endpoint to call (default: /weather)
            params: Additional query parameters
            
        Returns:
            List of extracted weather records
        """
        extracted_data = []

        if not self.api_key:
            logger.error("API key is required for OpenWeatherMap")
            return []

        try:
            logger.info(f"Extracting weather data from: {self.base_url}{endpoint}")

            # Get weather data for each city
            for city in self.cities:
                city = city.strip()
                if not city:
                    continue

                logger.info(f"Getting weather data for: {city}")

                # Prepare API parameters
                api_params = {
                    'q': city,
                    'appid': self.api_key,
                    'units': 'metric'  # Get temperature in Celsius
                }

                # Add any additional parameters
                if params:
                    api_params.update(params)

                url = f"{self.base_url}{endpoint}"

                response = self.session.get(url, params=api_params, timeout=30)

                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit for {city}, waiting...")
                    time.sleep(self.rate_limit_delay * 2)
                    continue

                # Handle API errors
                if response.status_code == 401:
                    logger.error("Invalid API key")
                    break
                elif response.status_code == 404:
                    logger.warning(f"City not found: {city}")
                    continue

                # Check for successful response
                response.raise_for_status()

                data = response.json()
                data['city_queried'] = city  # Add the city we queried for
                extracted_data.append(data)

                # Respect rate limits (60 calls/minute for free tier)
                time.sleep(self.rate_limit_delay)

            logger.info(f"Extracted weather data for {len(extracted_data)} cities")
            return extracted_data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return []

    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform extracted weather data for MongoDB compatibility
        
        Args:
            raw_data: Raw weather data from OpenWeatherMap API
            
        Returns:
            Transformed data ready for MongoDB
        """
        transformed_data = []

        try:
            for record in raw_data:
                # Extract main weather information
                main_weather = record.get('main', {})
                weather_desc = record.get('weather', [{}])[0]
                wind_info = record.get('wind', {})
                clouds_info = record.get('clouds', {})
                sys_info = record.get('sys', {})
                coord_info = record.get('coord', {})

                # Create transformed record with normalized structure
                transformed_record = {
                    # Original data for reference
                    'original_data': record,

                    # Location information
                    'city_name': record.get('name', ''),
                    'city_queried': record.get('city_queried', ''),
                    'country': sys_info.get('country', ''),
                    'coordinates': {
                        'latitude': coord_info.get('lat'),
                        'longitude': coord_info.get('lon')
                    },

                    # Weather conditions
                    'weather': {
                        'main': weather_desc.get('main', ''),
                        'description': weather_desc.get('description', ''),
                        'icon': weather_desc.get('icon', '')
                    },

                    # Temperature data
                    'temperature': {
                        'current_celsius': main_weather.get('temp'),
                        'feels_like_celsius': main_weather.get('feels_like'),
                        'min_celsius': main_weather.get('temp_min'),
                        'max_celsius': main_weather.get('temp_max'),
                        # Convert to Fahrenheit for analysis
                        'current_fahrenheit': self._celsius_to_fahrenheit(main_weather.get('temp')),
                        'feels_like_fahrenheit': self._celsius_to_fahrenheit(main_weather.get('feels_like'))
                    },

                    # Atmospheric conditions
                    'atmospheric': {
                        'pressure_hpa': main_weather.get('pressure'),
                        'humidity_percent': main_weather.get('humidity'),
                        'sea_level_hpa': main_weather.get('sea_level'),
                        'ground_level_hpa': main_weather.get('grnd_level'),
                        'visibility_meters': record.get('visibility')
                    },

                    # Wind information
                    'wind': {
                        'speed_mps': wind_info.get('speed'),
                        'direction_degrees': wind_info.get('deg'),
                        'gust_mps': wind_info.get('gust')
                    },

                    # Cloud information
                    'clouds': {
                        'coverage_percent': clouds_info.get('all')
                    },

                    # Sun times
                    'sun_times': {
                        'sunrise': datetime.fromtimestamp(sys_info.get('sunrise', 0)) if sys_info.get('sunrise') else None,
                        'sunset': datetime.fromtimestamp(sys_info.get('sunset', 0)) if sys_info.get('sunset') else None
                    },

                    # Computed fields
                    'computed_metrics': {
                        'heat_index_category': self._get_heat_index_category(main_weather.get('temp', 0)),
                        'humidity_category': self._get_humidity_category(main_weather.get('humidity', 0)),
                        'wind_category': self._get_wind_category(wind_info.get('speed', 0)),
                        'temperature_comfort': self._get_temperature_comfort(main_weather.get('temp', 0))
                    },

                    # ETL metadata
                    'etl_metadata': {
                        'ingestion_timestamp': datetime.now(timezone.utc),
                        'source_api': self.base_url,
                        'connector_version': '1.0.0',
                        'data_quality_score': self._calculate_weather_quality_score(record),
                        'api_call_timestamp': datetime.fromtimestamp(record.get('dt', 0)) if record.get('dt') else None
                    }
                }

                # Data validation
                if self._validate_weather_record(transformed_record):
                    transformed_data.append(transformed_record)
                else:
                    logger.warning(f"Invalid weather record skipped: {record.get('name', 'unknown')}")

            logger.info(f"Transformed weather data for {len(transformed_data)} cities")
            return transformed_data

        except Exception as e:
            logger.error(f"Weather data transformation failed: {str(e)}")
            return []

    def _celsius_to_fahrenheit(self, celsius: Optional[float]) -> Optional[float]:
        """Convert Celsius to Fahrenheit"""
        if celsius is None:
            return None
        return round((celsius * 9/5) + 32, 2)

    def _get_heat_index_category(self, temp_celsius: float) -> str:
        """Categorize temperature for heat index"""
        if temp_celsius < 10:
            return "Cold"
        elif temp_celsius < 20:
            return "Cool"
        elif temp_celsius < 30:
            return "Comfortable"
        elif temp_celsius < 35:
            return "Hot"
        else:
            return "Very Hot"

    def _get_humidity_category(self, humidity: float) -> str:
        """Categorize humidity levels"""
        if humidity < 30:
            return "Low"
        elif humidity < 50:
            return "Comfortable"
        elif humidity < 70:
            return "Moderate"
        else:
            return "High"

    def _get_wind_category(self, wind_speed: float) -> str:
        """Categorize wind speed (m/s)"""
        if wind_speed < 3:
            return "Light"
        elif wind_speed < 7:
            return "Moderate"
        elif wind_speed < 12:
            return "Strong"
        else:
            return "Very Strong"

    def _get_temperature_comfort(self, temp_celsius: float) -> str:
        """Determine temperature comfort level"""
        if temp_celsius < 15:
            return "Too Cold"
        elif temp_celsius <= 25:
            return "Comfortable"
        elif temp_celsius <= 30:
            return "Warm"
        else:
            return "Too Hot"

    def _calculate_weather_quality_score(self, record: Dict[str, Any]) -> float:
        """Calculate weather data quality score (0-1)"""
        score = 0.0
        total_checks = 8

        # Check required fields
        if record.get('name'): score += 0.125  # City name
        if record.get('main', {}).get('temp') is not None: score += 0.125  # Temperature
        if record.get('main', {}).get('humidity') is not None: score += 0.125  # Humidity
        if record.get('weather') and len(record['weather']) > 0: score += 0.125  # Weather description
        if record.get('wind', {}).get('speed') is not None: score += 0.125  # Wind speed
        if record.get('main', {}).get('pressure') is not None: score += 0.125  # Pressure
        if record.get('coord'): score += 0.125  # Coordinates
        if record.get('dt'): score += 0.125  # Timestamp

        return round(score, 2)

    def _validate_weather_record(self, record: Dict[str, Any]) -> bool:
        """Validate transformed weather record"""
        required_fields = ['city_name', 'temperature', 'weather', 'etl_metadata']
        return (all(field in record for field in required_fields) and 
                record['city_name'] and 
                record['temperature'].get('current_celsius') is not None)

    def load_data(self, transformed_data: List[Dict[str, Any]]) -> bool:
        """
        Load transformed data into MongoDB
        
        Args:
            transformed_data: Transformed data to load
            
        Returns:
            Success status
        """
        try:
            if not transformed_data:
                logger.warning("No data to load")
                return True

            # Insert data in batches for better performance
            batch_size = 100
            total_inserted = 0

            for i in range(0, len(transformed_data), batch_size):
                batch = transformed_data[i:i + batch_size]

                # Use upsert to handle duplicates (based on city_name and timestamp)
                for record in batch:
                    filter_query = {
                        'city_name': record['city_name'],
                        'etl_metadata.api_call_timestamp': record['etl_metadata']['api_call_timestamp']
                    }
                    update_query = {'$set': record}

                    result = self.collection.update_one(
                        filter_query, 
                        update_query, 
                        upsert=True
                    )

                    if result.upserted_id or result.modified_count > 0:
                        total_inserted += 1

            logger.info(f"Successfully loaded {total_inserted} records to MongoDB")
            return True

        except Exception as e:
            logger.error(f"Data loading failed: {str(e)}")
            return False

    def run_etl_pipeline(self, endpoint: str = '/weather') -> bool:
        """
        Run the complete ETL pipeline
        
        Args:
            endpoint: API endpoint to extract from
            
        Returns:
            Success status
        """
        try:
            logger.info("Starting ETL pipeline...")

            # Connect to MongoDB
            if not self.connect_to_mongodb():
                return False

            # Extract
            logger.info("Step 1: Extracting data...")
            raw_data = self.extract_data(endpoint)
            if not raw_data:
                logger.error("No data extracted")
                return False

            # Transform
            logger.info("Step 2: Transforming data...")
            transformed_data = self.transform_data(raw_data)
            if not transformed_data:
                logger.error("No data transformed")
                return False

            # Load
            logger.info("Step 3: Loading data...")
            if not self.load_data(transformed_data):
                return False

            logger.info("ETL pipeline completed successfully!")
            return True

        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            return False
        finally:
            # Close session but keep MongoDB connection open for stats
            self.session.close()

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        try:
            if self.collection is None:
                self.connect_to_mongodb()

            stats = {
                'total_records': self.collection.count_documents({}),
                'latest_ingestion': None,
                'quality_stats': {}
            }

            # Get latest ingestion timestamp
            latest_record = self.collection.find().sort('etl_metadata.ingestion_timestamp', -1).limit(1)
            latest_record = list(latest_record)
            if latest_record:
                stats['latest_ingestion'] = latest_record[0]['etl_metadata']['ingestion_timestamp']

            # Get quality score statistics
            pipeline = [
                {'$group': {
                    '_id': None,
                    'avg_quality': {'$avg': '$etl_metadata.data_quality_score'},
                    'min_quality': {'$min': '$etl_metadata.data_quality_score'},
                    'max_quality': {'$max': '$etl_metadata.data_quality_score'}
                }}
            ]

            quality_stats = list(self.collection.aggregate(pipeline))
            if quality_stats:
                stats['quality_stats'] = {
                    'average_score': round(quality_stats[0]['avg_quality'], 2),
                    'min_score': quality_stats[0]['min_quality'],
                    'max_score': quality_stats[0]['max_quality']
                }

            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}

def main():
    """Main function to run the ETL connector"""
    connector = ETLDataConnector()

    try:
        # Run ETL pipeline
        success = connector.run_etl_pipeline()

        if success:
            # Display statistics
            stats = connector.get_collection_stats()
            print("\n" + "="*50)
            print("ETL PIPELINE SUMMARY")
            print("="*50)
            print(f"Total records in collection: {stats.get('total_records', 'N/A')}")
            print(f"Latest ingestion: {stats.get('latest_ingestion', 'N/A')}")

            quality_stats = stats.get('quality_stats', {})
            if quality_stats:
                print(f"Average data quality score: {quality_stats.get('average_score', 'N/A')}")
                print(f"Quality score range: {quality_stats.get('min_score', 'N/A')} - {quality_stats.get('max_score', 'N/A')}")
        else:
            print("ETL pipeline failed. Check logs for details.")

    finally:
        # Cleanup MongoDB connection
        if connector.mongo_client:
            connector.mongo_client.close()

if __name__ == "__main__":
    main()
