import os
from typing import List, Optional
from colabdrive.logger import logger

class DriveOperations:
    """Class for Google Drive specific operations in Colab environment."""
    
    def __init__(self) -> None:
        """Initialize DriveOperations."""
        self.is_mounted = False
        self.mount_point = '/content/drive'
        self.is_colab = self._check_colab_environment()
        
    def _check_colab_environment(self) -> bool:
        """Check if running in Google Colab environment."""
        try:
            import google.colab
            return True
        except ImportError:
            logger.info("Not running in Colab environment")
            return False
        except Exception as e:
            logger.error(f"Error checking Colab environment: {e}")
            return False
        
    def mount_drive(self) -> bool:
        """Mount Google Drive in Colab."""
        if not self.is_colab:
            logger.log_warning("Drive mounting is only available in Google Colab")
            return False
            
        try:
            if not self.is_mounted:
                from google.colab import drive
                drive.mount(self.mount_point)
                self.is_mounted = True
                logger.log_info("Google Drive mounted successfully")
            return True
        except Exception as e:
            logger.log_error(f"Failed to mount Google Drive: {e}")
            return False
            
    def list_files(self, directory: str = '.') -> Optional[List[str]]:
        """List all files in a specified directory.
        
        Args:
            directory (str): Path to directory to list, defaults to root of My Drive
            
        Returns:
            Optional[List[str]]: List of filenames if successful, None if failed
        """
        try:
            files = os.listdir(directory)
            return files
        except FileNotFoundError:
            logger.log_error(f"Directory not found: {directory}")
            return None
        except Exception as e:
            logger.log_error(f"Error listing files: {e}")
            return None
