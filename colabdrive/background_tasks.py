## background_tasks.py

import concurrent.futures
from typing import Callable
import logging

# Import the logger instance from logger.py
from logger import logger

class BackgroundTasks:
    """Class for managing long-running background tasks."""

    def __init__(self) -> None:
        """Initializes the BackgroundTasks class."""
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def run_in_background(self, task: Callable) -> None:
        """
        Runs a given task in the background.

        Args:
            task (Callable): The task to run in the background.
        """
        try:
            logger.log_info("Starting background task.")
            future = self.executor.submit(task)
            future.add_done_callback(self._task_completed)
        except Exception as e:
            logger.log_error(f"Error starting background task: {e}")

    def _task_completed(self, future: concurrent.futures.Future) -> None:
        """Callback function to handle task completion."""
        try:
            result = future.result()  # This will raise an exception if the task failed
            logger.log_info(f"Background task completed with result: {result}")
        except Exception as e:
            logger.log_error(f"Background task failed: {e}")

    def shutdown(self) -> None:
        """Shuts down the background task executor."""
        logger.log_info("Shutting down background task executor.")
        self.executor.shutdown(wait=True)
