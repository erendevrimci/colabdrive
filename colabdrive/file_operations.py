## file_operations.py

import os
import shutil
import logging
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import mimetypes
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Import the logger instance from logger.py
from colabdrive.logger import logger

class FileOperations:
    """Class for handling file uploads, downloads, and conversions."""

    SUPPORTED_IMAGE_FORMATS = {
        'png': 'PNG image',
        'jpg': 'JPEG image', 
        'jpeg': 'JPEG image',
        'tiff': 'TIFF image',
        'bmp': 'BMP image',
        'gif': 'GIF image',
        'webp': 'WebP image'
    }

    SUPPORTED_DOCUMENT_FORMATS = {
        'pdf': 'PDF document',
        'txt': 'Text file',
        'md': 'Markdown file',
        'json': 'JSON file',
        'csv': 'CSV file'
    }

    VALID_CONVERSIONS = {
        'image': {
            'source': ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp'],
            'target': ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp']
        },
        'document': {
            'source': ['txt', 'md', 'json', 'csv'],
            'target': ['txt', 'md', 'json', 'csv', 'pdf']
        }
    }

    def __init__(self) -> None:
        """Initializes the FileOperations class."""
        self.gauth = None
        self.drive = None
        self.base_dir = os.path.expanduser("~/colabdrive_files")
        self.downloads_dir = os.path.join(self.base_dir, "downloads")
        self.uploads_dir = os.path.join(self.base_dir, "uploads")
        self.converted_dir = os.path.join(self.base_dir, "converted")
        
        # Create necessary directories
        for directory in [self.base_dir, self.downloads_dir, self.uploads_dir, self.converted_dir]:
            os.makedirs(directory, exist_ok=True)
            
        try:
            self._setup_drive()
        except Exception as e:
            logger.error(f"Google Drive setup failed: {e}. Some features will be limited.")
            
    def _setup_drive(self) -> None:
        """Sets up Google Drive authentication if credentials are available."""
        if os.path.exists('client_secrets.json'):
            self.gauth = GoogleAuth()
            self.drive = self._authenticate_drive()

    def _authenticate_drive(self) -> GoogleDrive:
        """Authenticates and creates a Google Drive instance.

        Returns:
            GoogleDrive: Authenticated Google Drive instance.
        """
        try:
            self.gauth.LocalWebserverAuth()  # Creates a local webserver for authentication
            logger.info("Google Drive authentication successful.")
            return GoogleDrive(self.gauth)
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            raise

    def upload_file(self, file: str, destination_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Uploads a file to Google Drive.

        Args:
            file (str): The path to the file to upload.
            destination_dir (str, optional): The destination directory in Google Drive.

        Returns:
            Tuple[bool, str]: (Success status, Message with details)
        """
        if not self.drive:
            return False, "Google Drive not configured. Upload not available."
            
        if not os.path.exists(file):
            return False, f"File not found: {file}"
            
        try:
            # First copy to uploads directory
            filename = os.path.basename(file)
            upload_path = os.path.join(self.uploads_dir, filename)
            shutil.copy2(file, upload_path)
            
            # Prepare drive path
            drive_path = destination_dir if destination_dir else '/'
            file_metadata = {
                'title': filename,
                'parents': [{'id': drive_path}] if drive_path != '/' else []
            }
            
            # Upload to drive
            media = MediaFileUpload(upload_path, resumable=True)
            uploaded_file = self.drive.CreateFile(file_metadata)
            uploaded_file.SetContentMedia(media)
            uploaded_file.Upload()
            
            logger.info(f"File uploaded successfully: {filename} to {drive_path}")
            return True, f"Successfully uploaded {filename} to {drive_path}"
            
        except Exception as e:
            error_msg = f"Failed to upload file {file}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def list_available_files(self) -> List[Dict[str, str]]:
        """Lists all available files in Google Drive.

        Returns:
            List[Dict[str, str]]: List of files with their IDs and names
        """
        if not self.drive:
            return []
            
        try:
            file_list = self.drive.ListFile({'q': "trashed=false"}).GetList()
            return [{'id': f['id'], 'title': f['title'], 'mimeType': f['mimeType']} 
                   for f in file_list]
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def download_file(self, file_id: str, destination_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Downloads a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.
            destination_dir (str, optional): Custom destination directory.

        Returns:
            Tuple[bool, str]: (Success status, Message with details)
        """
        if not self.drive:
            return False, "Error: Google Drive not configured. Please authenticate first."
            
        if not self.gauth or not self.gauth.credentials:
            return False, "Error: Not authenticated with Google Drive. Please authenticate first."
            
        try:
            # Verify file exists and is accessible
            try:
                downloaded_file = self.drive.CreateFile({'id': file_id})
                downloaded_file.FetchMetadata()
            except Exception as e:
                if 'accessNotConfigured' in str(e):
                    return False, "Error: Google Drive API not properly configured. Please check your credentials."
                elif 'File not found' in str(e):
                    return False, f"Error: File with ID {file_id} not found"
                else:
                    return False, f"Error accessing file: {str(e)}"
                    
            filename = downloaded_file['title']
            
            # Validate filename
            if not filename or not filename.strip():
                return False, "Error: Invalid filename received from Google Drive"
                
            # Determine destination path
            final_destination_dir = destination_dir if destination_dir else self.downloads_dir
            os.makedirs(final_destination_dir, exist_ok=True)
            destination_path = os.path.join(final_destination_dir, filename)
            
            # Download file with progress tracking
            downloaded_file.GetContentFile(destination_path)
            
            # Verify download
            if not os.path.exists(destination_path):
                return False, "Error: Download failed - file not created"
                
            if os.path.getsize(destination_path) == 0:
                os.remove(destination_path)
                return False, "Error: Download failed - empty file"
                
            success_msg = f"Success: File downloaded to {destination_path}"
            logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error downloading file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_supported_formats(self) -> Dict[str, Dict[str, List[str]]]:
        """Returns supported formats for conversion.

        Returns:
            Dict describing supported formats and valid conversions
        """
        return self.VALID_CONVERSIONS

    def convert_file(self, input_file: str, output_format: str, 
                    output_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Converts a file to a specified format.

        Args:
            input_file (str): The path to the input file.
            output_format (str): The desired output format.
            output_dir (str, optional): Custom output directory.

        Returns:
            Tuple[bool, str]: (Success status, Message with details)
        """
        # Input validation
        if not os.path.exists(input_file):
            return False, f"Error: Input file not found: {input_file}"
            
        if not os.path.isfile(input_file):
            return False, f"Error: {input_file} is not a file"
            
        # Format validation
        input_ext = os.path.splitext(input_file)[1][1:].lower()
        output_format = output_format.lower().strip('.')
        
        if not input_ext:
            return False, "Error: Input file has no extension"
            
        if not output_format:
            return False, "Error: Output format not specified"
            
        # Check if conversion is supported
        conversion_category = None
        for category, formats in self.VALID_CONVERSIONS.items():
            if input_ext in formats['source'] and output_format in formats['target']:
                conversion_category = category
                break
                
        if not conversion_category:
            supported_formats = {cat: self.VALID_CONVERSIONS[cat] for cat in self.VALID_CONVERSIONS}
            return False, f"Error: Conversion from {input_ext} to {output_format} is not supported.\nSupported conversions: {supported_formats}"
            
        try:
            # Determine output path
            filename = os.path.basename(input_file)
            base_name = os.path.splitext(filename)[0]
            final_output_dir = output_dir if output_dir else self.converted_dir
            os.makedirs(final_output_dir, exist_ok=True)
            output_path = os.path.join(final_output_dir, f"{base_name}.{output_format}")
            
            # Handle image conversions
            if input_ext in self.SUPPORTED_IMAGE_FORMATS and output_format in self.SUPPORTED_IMAGE_FORMATS:
                with Image.open(input_file) as img:
                    img.save(output_path)
                    
            # Handle document conversions
            elif input_ext in self.SUPPORTED_DOCUMENT_FORMATS and output_format in self.SUPPORTED_DOCUMENT_FORMATS:
                # For now, just copy text-based files
                if input_ext in ['txt', 'md', 'json', 'csv'] and output_format in ['txt', 'md', 'json', 'csv']:
                    shutil.copy2(input_file, output_path)
                else:
                    return False, f"Document conversion from {input_ext} to {output_format} not implemented yet"
            
            success_msg = f"File converted successfully: {output_path}"
            logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Failed to convert file {input_file}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
