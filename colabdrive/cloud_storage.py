## cloud_storage.py
import os
from typing import Optional
import boto3
import dropbox
from colabdrive.config import config
from googleapiclient.http import MediaFileUpload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Import the logger instance from logger.py
from logger import logger


class CloudStorage:
    """Class for managing file operations with Google Drive, S3, and Dropbox.
    Handles authentication and file operations for multiple cloud storage services.
    """

    def __init__(self) -> None:
        """Initializes the CloudStorage class."""
        self.project_id = config.get('project_id')
        if not self.project_id:
            raise ValueError("Project ID not configured")
        self.drive = self._authenticate_drive()
        self.s3_client = self._initialize_s3()
        self.dropbox_client = self._initialize_dropbox()

    def _authenticate_drive(self) -> Optional[GoogleDrive]:
        """Authenticates and creates a Google Drive instance.

        Returns:
            Optional[GoogleDrive]: Authenticated Google Drive instance or None if authentication fails.
        """
        try:
            gauth = GoogleAuth()
            
            # Set up authentication settings
            gauth.settings['get_refresh_token'] = True
            gauth.settings['oauth_scope'] = ['https://www.googleapis.com/auth/drive']
            gauth.settings['client_config_file'] = 'client_secrets.json'
            
            # Create credentials directory in user's home
            creds_dir = os.path.join(os.path.expanduser('~'), '.colabdrive')
            creds_file = os.path.join(creds_dir, 'mycreds.txt')
            os.makedirs(creds_dir, exist_ok=True)
            
            # Try to load existing credentials
            gauth.LoadCredentialsFile(creds_file)
            
            if gauth.credentials is None:
                # No credentials found, start new authentication
                gauth.LocalWebserverAuth(port_numbers=[8080])
            elif gauth.access_token_expired:
                # Refresh expired token
                gauth.Refresh()
            else:
                # Reauthorize with existing credentials
                gauth.Authorize()
            
            # Save the current credentials
            gauth.SaveCredentialsFile(creds_file)
            
            logger.info("Google Drive authentication successful.")
            return GoogleDrive(gauth)
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            return None

    def _initialize_s3(self) -> boto3.client:
        """Initializes the S3 client.

        Returns:
            boto3.client: S3 client instance.
        """
        try:
            s3_client = boto3.client('s3')
            logger.info("S3 client initialized successfully.")
            return s3_client
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def _initialize_dropbox(self) -> dropbox.Dropbox:
        """Initializes the Dropbox client.

        Returns:
            dropbox.Dropbox: Dropbox client instance.
        """
        try:
            dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')  # Replace with your access token
            logger.info("Dropbox client initialized successfully.")
            return dbx
        except Exception as e:
            logger.error(f"Failed to initialize Dropbox client: {e}")
            raise

    def upload_to_drive(self, file: str) -> bool:
        """Uploads a file to Google Drive.

        Args:
            file (str): The path to the file to upload.

        Returns:
            bool: True if upload is successful, False otherwise.
        """
        try:
            file_metadata = {'title': file.split('/')[-1]}
            media = MediaFileUpload(file, resumable=True)
            uploaded_file = self.drive.CreateFile(file_metadata)
            uploaded_file.SetContentMedia(media)
            uploaded_file.Upload()
            logger.info(f"File uploaded to Google Drive successfully: {file}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to Google Drive {file}: {e}")
            return False

    def download_from_drive(self, file_id: str, destination: str) -> bool:
        """Downloads a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.
            destination (str): The path where the file will be saved.

        Returns:
            bool: True if download is successful, False otherwise.
        """
        try:
            downloaded_file = self.drive.CreateFile({'id': file_id})
            downloaded_file.GetContentFile(destination)
            logger.info(f"File downloaded from Google Drive successfully: {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file from Google Drive {file_id}: {e}")
            return False

    def upload_to_s3(self, file: str, bucket_name: str) -> bool:
        """Uploads a file to S3.

        Args:
            file (str): The path to the file to upload.
            bucket_name (str): The name of the S3 bucket.

        Returns:
            bool: True if upload is successful, False otherwise.
        """
        try:
            self.s3_client.upload_file(file, bucket_name, file.split('/')[-1])
            logger.info(f"File uploaded to S3 successfully: {file}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to S3 {file}: {e}")
            return False

    def download_from_s3(self, file_name: str, bucket_name: str, destination: str) -> bool:
        """Downloads a file from S3.

        Args:
            file_name (str): The name of the file to download.
            bucket_name (str): The name of the S3 bucket.
            destination (str): The path where the file will be saved.

        Returns:
            bool: True if download is successful, False otherwise.
        """
        try:
            self.s3_client.download_file(bucket_name, file_name, destination)
            logger.info(f"File downloaded from S3 successfully: {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file from S3 {file_name}: {e}")
            return False

    def upload_to_dropbox(self, file: str) -> bool:
        """Uploads a file to Dropbox.

        Args:
            file (str): The path to the file to upload.

        Returns:
            bool: True if upload is successful, False otherwise.
        """
        try:
            with open(file, 'rb') as f:
                self.dropbox_client.files_upload(f.read(), '/' + file.split('/')[-1])
            logger.info(f"File uploaded to Dropbox successfully: {file}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to Dropbox {file}: {e}")
            return False

    def download_from_dropbox(self, file_name: str, destination: str) -> bool:
        """Downloads a file from Dropbox.

        Args:
            file_name (str): The name of the file to download.
            destination (str): The path where the file will be saved.

        Returns:
            bool: True if download is successful, False otherwise.
        """
        try:
            with open(destination, 'wb') as f:
                metadata, res = self.dropbox_client.files_download(path='/' + file_name)
                f.write(res.content)
            logger.info(f"File downloaded from Dropbox successfully: {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file from Dropbox {file_name}: {e}")
            return False
