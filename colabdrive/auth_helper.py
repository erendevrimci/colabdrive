import os
from typing import Optional
from pydrive.auth import GoogleAuth
from colabdrive.logger import logger

def verify_credentials() -> bool:
    """Verify if credentials file exists and is valid.
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        creds_dir = os.path.join(os.path.expanduser('~'), '.colabdrive')
        creds_file = os.path.join(creds_dir, 'mycreds.txt')
        
        # Check if credentials file exists
        if not os.path.exists(creds_file):
            logger.warning("No credentials file found")
            return False
            
        # Try to load credentials
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(creds_file)
        
        # Check if credentials are valid
        if gauth.credentials is None:
            logger.warning("Invalid credentials")
            return False
            
        # Check if token is expired
        if gauth.access_token_expired:
            try:
                gauth.Refresh()
                gauth.SaveCredentialsFile(creds_file)
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error verifying credentials: {e}")
        return False

def clear_credentials() -> None:
    """Remove existing credentials file."""
    try:
        creds_file = os.path.join(os.path.expanduser('~'), '.colabdrive', 'mycreds.txt')
        if os.path.exists(creds_file):
            os.remove(creds_file)
            logger.info("Credentials cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing credentials: {e}")
