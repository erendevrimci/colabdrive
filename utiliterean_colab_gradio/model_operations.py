import os
import requests
from typing import Optional
from huggingface_hub import snapshot_download
from git import Repo
from utiliterean_colab_gradio.logger import logger

class ModelOperations:
    """Class for handling model downloads from various sources."""
    
    def __init__(self) -> None:
        """Initialize ModelOperations."""
        self.default_path = os.path.join('/content/drive/My Drive', 'models')
        os.makedirs(self.default_path, exist_ok=True)
        self.chunk_size = 8192
        
    def download_from_huggingface(self, model_name: str, file_name: str) -> Optional[str]:
        """Download a specific file from HuggingFace."""
        try:
            base_url = f"https://huggingface.co/{model_name}/resolve/main/{file_name}"
            destination_path = os.path.join(self.default_path, file_name)
            
            response = requests.get(base_url, stream=True)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                with open(destination_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                logger.log_info(f"Downloaded {file_name} from HuggingFace")
                return destination_path
            else:
                logger.log_error(f"Failed to download from HuggingFace: {response.status_code}")
                return None
        except Exception as e:
            logger.log_error(f"Error downloading from HuggingFace: {e}")
            return None
            
    def clone_github_repo(self, repo_url: str) -> Optional[str]:
        """Clone a GitHub repository."""
        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            destination_path = os.path.join(self.default_path, repo_name)
            Repo.clone_from(repo_url, destination_path)
            logger.log_info(f"Cloned repository to {destination_path}")
            return destination_path
        except Exception as e:
            logger.log_error(f"Error cloning repository: {e}")
            return None
            
    def download_civitai_model(self, model_url: str) -> Optional[str]:
        """Download a model from CivitAI."""
        try:
            model_name = model_url.split('/')[-1]
            destination_path = os.path.join(self.default_path, model_name)
            
            response = requests.get(model_url, stream=True)
            if response.status_code == 200:
                with open(destination_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.log_info(f"Downloaded model from CivitAI to {destination_path}")
                return destination_path
            else:
                logger.log_error(f"Failed to download from CivitAI: {response.status_code}")
                return None
        except Exception as e:
            logger.log_error(f"Error downloading from CivitAI: {e}")
            return None
