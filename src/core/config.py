import os
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from environment variables and .env file.
    """
    load_dotenv()
    
    config = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GOOGLE_CSE_ID": os.getenv("GOOGLE_CSE_ID"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
        # Add other keys here
    }
    
    return config
