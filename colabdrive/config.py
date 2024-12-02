import os
from typing import Dict, Any

class Config:
    """Configuration management for different environments."""
    
    def __init__(self) -> None:
        self.is_colab = self._check_colab_environment()
        self.env = "colab" if self.is_colab else "local"
        self.config = self._load_config()
    
    def _check_colab_environment(self) -> bool:
        """Check if running in Google Colab environment."""
        try:
            import google.colab
            return True
        except ImportError:
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        base_config = {
            "local": {
                "model_path": os.path.join(os.path.expanduser('~'), 'models'),
                "drive_mount_point": None,
                "server_name": "127.0.0.1",
                "server_port": 7860,  # Must match OAuth redirect URI port
                "allowed_paths": [os.path.expanduser('~')]
            },
            "colab": {
                "model_path": "/content/drive/My Drive/models",
                "drive_mount_point": "/content/drive",
                "server_name": "127.0.0.1",
                "server_port": 7860,
                "allowed_paths": ["/content", "/content/drive"]
            }
        }
        return base_config[self.env]
    
    def get(self, key: str) -> Any:
        """Get configuration value by key."""
        return self.config.get(key)

# Create a singleton instance
config = Config()
