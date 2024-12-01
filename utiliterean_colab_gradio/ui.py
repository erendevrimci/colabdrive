## ui.py

import gradio as gr
from typing import Optional
from logger import logger
from file_operations import FileOperations

class UI:
    """Class for creating the user interface and displaying progress and errors."""

    def __init__(self) -> None:
        """Initializes the UI class and the FileOperations instance."""
        self.interface: Optional[gr.Interface] = None
        self.file_operations = FileOperations()

    def create_interface(self) -> None:
        """Creates the user interface for the application."""
        with gr.Blocks() as self.interface:
            gr.Markdown("## File Operations")
            with gr.Row():
                self.upload_file_input = gr.File(label="Upload File")
                self.upload_button = gr.Button("Upload")
                self.upload_status = gr.Textbox(label="Upload Status", interactive=False)

            with gr.Row():
                self.download_file_input = gr.Textbox(label="File ID to Download")
                self.download_button = gr.Button("Download")
                self.download_status = gr.Textbox(label="Download Status", interactive=False)

            with gr.Row():
                self.convert_file_input = gr.File(label="File to Convert")
                self.output_format_input = gr.Textbox(label="Output Format")
                self.convert_button = gr.Button("Convert")
                self.convert_status = gr.Textbox(label="Conversion Status", interactive=False)

            self.upload_button.click(self.upload_file, inputs=self.upload_file_input, outputs=self.upload_status)
            self.download_button.click(self.download_file, inputs=self.download_file_input, outputs=self.download_status)
            self.convert_button.click(self.convert_file, inputs=[self.convert_file_input, self.output_format_input], outputs=self.convert_status)

        logger.log_info("User interface created successfully.")

    def upload_file(self, file: str) -> str:
        """Handles file upload and updates the status.

        Args:
            file (str): The path to the file to upload.

        Returns:
            str: Status message indicating the result of the upload.
        """
        logger.log_info(f"Attempting to upload file: {file}")
        success = self.file_operations.upload_file(file)
        if success:
            logger.log_info(f"File uploaded successfully: {file}")
            return "Upload successful!"
        else:
            logger.log_error(f"Failed to upload file: {file}")
            return "Upload failed."

    def download_file(self, file_id: str) -> str:
        """Handles file download and updates the status.

        Args:
            file_id (str): The ID of the file to download.

        Returns:
            str: Status message indicating the result of the download.
        """
        logger.log_info(f"Attempting to download file with ID: {file_id}")
        destination = "path/to/save/file"  # Define the destination path
        success = self.file_operations.download_file(file_id, destination)
        if success:
            logger.log_info(f"File downloaded successfully: {file_id}")
            return "Download successful!"
        else:
            logger.log_error(f"Failed to download file with ID: {file_id}")
            return "Download failed."

    def convert_file(self, input_file: str, output_format: str) -> str:
        """Handles file conversion and updates the status.

        Args:
            input_file (str): The path to the input file.
            output_format (str): The desired output format.

        Returns:
            str: Status message indicating the result of the conversion.
        """
        logger.log_info(f"Attempting to convert file: {input_file} to {output_format}")
        success = self.file_operations.convert_file(input_file, output_format)
        if success:
            logger.log_info(f"File converted successfully: {input_file} to {output_format}")
            return "Conversion successful!"
        else:
            logger.log_error(f"Failed to convert file: {input_file}")
            return "Conversion failed."

    def launch(self) -> None:
        """Launches the Gradio interface."""
        if self.interface is not None:
            self.interface.launch()
            logger.log_info("Gradio interface launched.")

# Create a UI instance and launch the interface
ui = UI()
ui.create_interface()
ui.launch()
