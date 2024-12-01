## main.py

import logging
from file_operations import FileOperations
from cloud_storage import CloudStorage
from model_management import ModelManagement
from ui import UI
from background_tasks import BackgroundTasks
from logger import logger

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
