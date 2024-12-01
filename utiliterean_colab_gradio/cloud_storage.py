## cloud_storage.py

import logging
from typing import Optional
import boto3
import dropbox
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Import the logger instance from logger.py
from logger import logger

class CloudStorage:
    """Class for managing file operations with Google Drive, S3, and Dropbox."""

    def __init__(self) -> None:
        """Initializes the CloudStorage class."""
        self.drive = self._authenticate_drive()
        self.s3_client = self._initialize_s3()
        self.dropbox_client = self._initialize_dropbox()

    def _authenticate_drive(self) -> GoogleDrive:
        """Authenticates and creates a Google Drive instance.

        Returns:
            GoogleDrive: Authenticated Google Drive instance.
        """
        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()  # Creates a local webserver for authentication
            logger.log_info("Google Drive authentication successful.")
            return GoogleDrive(gauth)
        except Exception as e:
            logger.log_error(f"Google Drive authentication failed: {e}")
            raise

    def _initialize_s3(self) -> boto3.client:
        """Initializes the S3 client.

        Returns:
            boto3.client: S3 client instance.
        """
        try:
            s3_client = boto3.client('s3')
            logger.log_info("S3 client initialized successfully.")
            return s3_client
        except Exception as e:
            logger.log_error(f"Failed to initialize S3 client: {e}")
            raise

    def _initialize_dropbox(self) -> dropbox.Dropbox:
        """Initializes the Dropbox client.

        Returns:
            dropbox.Dropbox: Dropbox client instance.
        """
        try:
            dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')  # Replace with your access token
            logger.log_info("Dropbox client initialized successfully.")
            return dbx
        except Exception as e:
            logger.log_error(f"Failed to initialize Dropbox client: {e}")
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
            logger.log_info(f"File uploaded to Google Drive successfully: {file}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to upload file to Google Drive {file}: {e}")
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
            logger.log_info(f"File downloaded from Google Drive successfully: {destination}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to download file from Google Drive {file_id}: {e}")
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
            logger.log_info(f"File uploaded to S3 successfully: {file}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to upload file to S3 {file}: {e}")
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
            logger.log_info(f"File downloaded from S3 successfully: {destination}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to download file from S3 {file_name}: {e}")
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
            logger.log_info(f"File uploaded to Dropbox successfully: {file}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to upload file to Dropbox {file}: {e}")
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
            logger.log_info(f"File downloaded from Dropbox successfully: {destination}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to download file from Dropbox {file_name}: {e}")
            return False
