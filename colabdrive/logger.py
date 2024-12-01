## logger.py

import logging
import os

class Logger:
    """Logger class for setting up logging configuration."""

    def __init__(self, log_file: str = "app.log", level: int = logging.INFO) -> None:
        """
        Initializes the Logger with specified log file and logging level.

        Args:
            log_file (str): The name of the log file. Defaults to "app.log".
            level (int): The logging level. Defaults to logging.INFO.
        """
        self.log_file = log_file
        self.level = level
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Sets up the logging configuration."""
        logging.basicConfig(
            filename=self.log_file,
            filemode='a',  # Append mode
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=self.level
        )
        logging.info("Logging is set up.")

    def log_info(self, message: str) -> None:
        """Logs an informational message.

        Args:
            message (str): The message to log.
        """
        logging.info(message)

    def log_warning(self, message: str) -> None:
        """Logs a warning message.

        Args:
            message (str): The message to log.
        """
        logging.warning(message)

    def log_error(self, message: str) -> None:
        """Logs an error message.

        Args:
            message (str): The message to log.
        """
        logging.error(message)

    def log_debug(self, message: str) -> None:
        """Logs a debug message.

        Args:
            message (str): The message to log.
        """
        logging.debug(message)

# Create a logger instance with root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
