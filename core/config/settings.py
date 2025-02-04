import os
from dotenv import load_dotenv

load_dotenv()

def get_google_maps_api_key():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    return api_key