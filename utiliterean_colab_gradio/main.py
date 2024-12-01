## main.py

import logging
from utiliterean_colab_gradio.file_operations import FileOperations
from utiliterean_colab_gradio.cloud_storage import CloudStorage
from utiliterean_colab_gradio.model_management import ModelManagement
from utiliterean_colab_gradio.ui import UI
from utiliterean_colab_gradio.background_tasks import BackgroundTasks
from utiliterean_colab_gradio.logger import logger

class Main:
    """Main class that orchestrates the application flow."""

    def __init__(self) -> None:
        """Initializes the Main class and its components."""
        self.file_operations = FileOperations()
        self.cloud_storage = CloudStorage()
        self.model_management = ModelManagement()
        self.ui = UI()
        self.background_tasks = BackgroundTasks()

    def run(self) -> None:
        """Runs the main application."""
        logger.log_info("Starting the application.")
        self.ui.create_interface()
        self.ui.launch()
        logger.log_info("Application is running.")

if __name__ == "__main__":
    main_app = Main()
    main_app.run()
