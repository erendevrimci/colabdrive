## ui.py

import gradio as gr
from typing import Optional
from gradio.themes.utils import colors
from gradio.themes import Base
from utiliterean_colab_gradio.logger import logger
from utiliterean_colab_gradio.file_operations import FileOperations
from utiliterean_colab_gradio.drive_operations import DriveOperations
from utiliterean_colab_gradio.model_operations import ModelOperations

class UI:
    """Class for creating the user interface and displaying progress and errors."""

    def __init__(self) -> None:
        """Initializes the UI class and its components."""
        self.interface: Optional[gr.Interface] = None
        self.file_operations = FileOperations()
        self.drive_operations = DriveOperations()
        try:
            self.model_operations = ModelOperations()
        except Exception as e:
            logger.log_error(f"Failed to initialize ModelOperations: {e}")
            self.model_operations = None

    def mount_drive(self) -> str:
        """Mount Google Drive and return status.

        Returns:
            str: Status message indicating mount result
        """
        success = self.drive_operations.mount_drive()
        return "Drive mounted successfully!" if success else "Failed to mount drive"

    def list_directory(self, directory: str) -> str:
        """List files in the specified directory.

        Args:
            directory (str): Path to directory to list

        Returns:
            str: Newline-separated list of files or error message
        """
        files = self.drive_operations.list_files(directory)
        if files:
            return "\n".join(files)
        return "Failed to list files"

    def download_from_huggingface(self, model_name: str, file_name: str) -> str:
        """Download a file from HuggingFace.
        
        Args:
            model_name (str): Name of the model/repo on HuggingFace
            file_name (str): Name of file to download
            
        Returns:
            str: Status message indicating download result
        """
        if not self.model_operations:
            return "Model operations not available"
        result = self.model_operations.download_from_huggingface(model_name, file_name)
        return f"Downloaded to {result}" if result else "Download failed"

    def clone_github_repo(self, repo_url: str) -> str:
        """Clone a GitHub repository.
        
        Args:
            repo_url (str): URL of GitHub repository
            
        Returns:
            str: Status message indicating clone result
        """
        result = self.model_operations.clone_github_repo(repo_url)
        return f"Cloned to {result}" if result else "Clone failed"

    def download_from_civitai(self, model_url: str) -> str:
        """Download a model from CivitAI.
        
        Args:
            model_url (str): URL of the model on CivitAI
            
        Returns:
            str: Status message indicating download result
        """
        result = self.model_operations.download_civitai_model(model_url)
        return f"Downloaded to {result}" if result else "Download failed"

    def create_interface(self) -> None:
        """Creates the user interface for the application."""
        custom_theme = Base(
            primary_hue=colors.blue,
            secondary_hue=colors.slate,
            neutral_hue=colors.gray,
            font=("Helvetica", "ui-sans-serif"),
            spacing_size={
                "xxs": 2,
                "xs": 4, 
                "sm": 6,
                "md": 8,
                "lg": 12,
                "xl": 16,
                "xxl": 20
            },
        )
        
        with gr.Blocks(
            title="Utiliterean Colab Assistant",
            theme=custom_theme,
            css=".container { max-width: 1000px; margin: auto; padding: 2rem; }"
        ) as self.interface:
            gr.Markdown(
                """
                # 🚀 Utiliterean Colab Assistant
                Your all-in-one tool for managing models and files in Colab
                """
            )
            
            with gr.Tabs():
                with gr.Tab("📁 Drive Operations", id=1):
                    with gr.Group():
                        with gr.Row():
                            self.mount_button = gr.Button("🔌 Mount Google Drive", variant="primary")
                            self.mount_status = gr.Textbox(
                                label="Mount Status",
                                interactive=False,
                                container=False
                            )
                        
                        with gr.Row():
                            with gr.Column(scale=3):
                                self.list_files_input = gr.Textbox(
                                    label="Directory Path",
                                    value="/content/drive/My Drive",
                                    container=True
                                )
                            with gr.Column(scale=1):
                                self.list_files_button = gr.Button("📋 List Files", variant="secondary")
                        
                        self.files_list = gr.Textbox(
                            label="Files",
                            interactive=False,
                            lines=10,
                            container=True
                        )
                
                with gr.Tab("🤖 Model Operations", id=2):
                    with gr.Group():
                        gr.Markdown("### HuggingFace Downloads")
                        with gr.Row():
                            with gr.Column(scale=2):
                                self.hf_model_name = gr.Textbox(
                                    label="Model Name",
                                    placeholder="e.g., bert-base-uncased"
                                )
                                self.hf_file_name = gr.Textbox(
                                    label="File Name",
                                    placeholder="e.g., config.json"
                                )
                            with gr.Column(scale=1):
                                self.hf_download_button = gr.Button("🤗 Download from HuggingFace", variant="primary")
                                self.hf_status = gr.Textbox(label="Status", interactive=False)
                        
                        gr.Markdown("### GitHub Repository")
                        with gr.Row():
                            with gr.Column(scale=2):
                                self.github_url = gr.Textbox(
                                    label="Repository URL",
                                    placeholder="https://github.com/username/repo"
                                )
                            with gr.Column(scale=1):
                                self.github_clone_button = gr.Button("📦 Clone Repository", variant="primary")
                                self.github_status = gr.Textbox(label="Status", interactive=False)
                        
                        gr.Markdown("### CivitAI Models")
                        with gr.Row():
                            with gr.Column(scale=2):
                                self.civitai_url = gr.Textbox(
                                    label="Model URL",
                                    placeholder="https://civitai.com/models/..."
                                )
                            with gr.Column(scale=1):
                                self.civitai_download_button = gr.Button("⬇️ Download from CivitAI", variant="primary")
                                self.civitai_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Tab("📄 File Operations", id=3):
                    with gr.Group():
                        with gr.Accordion("Upload", open=True):
                            with gr.Row():
                                with gr.Column(scale=2):
                                    self.upload_file_input = gr.File(
                                        label="Select File",
                                        file_count="single"
                                    )
                                with gr.Column(scale=1):
                                    self.upload_button = gr.Button("⬆️ Upload", variant="primary")
                                    self.upload_status = gr.Textbox(label="Status", interactive=False)

                        with gr.Accordion("Download", open=True):
                            with gr.Row():
                                with gr.Column(scale=2):
                                    self.download_file_input = gr.Textbox(
                                        label="File ID",
                                        placeholder="Enter file ID to download"
                                    )
                                with gr.Column(scale=1):
                                    self.download_button = gr.Button("⬇️ Download", variant="primary")
                                    self.download_status = gr.Textbox(label="Status", interactive=False)

                        with gr.Accordion("Convert", open=True):
                            with gr.Row():
                                with gr.Column(scale=2):
                                    self.convert_file_input = gr.File(
                                        label="Select File",
                                        file_count="single"
                                    )
                                    self.output_format_input = gr.Textbox(
                                        label="Output Format",
                                        placeholder="e.g., pdf, jpg, png"
                                    )
                                with gr.Column(scale=1):
                                    self.convert_button = gr.Button("🔄 Convert", variant="primary")
                                    self.convert_status = gr.Textbox(label="Status", interactive=False)

            # Connect all the new buttons
            self.mount_button.click(self.mount_drive, outputs=self.mount_status)
            self.list_files_button.click(self.list_directory, inputs=self.list_files_input, outputs=self.files_list)
            self.hf_download_button.click(self.download_from_huggingface, 
                                        inputs=[self.hf_model_name, self.hf_file_name],
                                        outputs=self.hf_status)
            self.github_clone_button.click(self.clone_github_repo,
                                         inputs=self.github_url,
                                         outputs=self.github_status)
            self.civitai_download_button.click(self.download_from_civitai,
                                             inputs=self.civitai_url,
                                             outputs=self.civitai_status)
            
            # Original buttons
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
