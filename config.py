import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    config = {}
    config['BASE_URL'] = os.getenv('API_BASE_URL')
    config['API_KEY'] = os.getenv('X-OTX-API-KEY')
    config['PULSES_SUBSCRIBED_ENDPOINT'] = os.getenv('PULSES_SUBSCRIBED_ENDPOINT')
    config['PAGE_LIMIT'] = int(os.getenv('PAGE_LIMIT'))
    config['MONGO_URL'] = os.getenv('MONGO_URL')
    config['MONGO_DB'] = os.getenv('MONGO_DB')


    return config


