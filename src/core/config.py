import os
from src.core.secrets_manager import SecretsManager

def load_config():
    """
    Load configuration with secure credential handling.
    Credentials are loaded from:
    1. Environment variables (priority)
    2. Encrypted local file
    """
    secrets = SecretsManager()
    
    config = {
        "GOOGLE_API_KEY": secrets.get_credential("google_api_key"),
        "GOOGLE_CSE_ID": secrets.get_credential("google_cse_id"),
        "TWITTER_BEARER_TOKEN": secrets.get_credential("twitter_bearer_token"),
    }
    
    return config
