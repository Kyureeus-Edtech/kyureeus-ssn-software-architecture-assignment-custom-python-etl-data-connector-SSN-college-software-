import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

malshareConfig = {
    "API_KEY": os.getenv('MALSHARE_API_KEY'),
    "BASE_URL": os.getenv('MALSHARE_BASE_URL')
}