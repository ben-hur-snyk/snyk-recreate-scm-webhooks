import logging
import sys
import os
from config import Config

class Logger:
    def __init__(self, config: Config):
        self.config = config
        self._instance = None

        self._logger = None
    
    @staticmethod
    def init(config: Config):
        Logger._instance = Logger(config).create()

    @staticmethod
    def get_instance():
        return Logger._instance

    def create(self):
        # 1. Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  # Set the minimum level for the logger

        # 2. Define the formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(message)s'
        )

        # --- Setup FileHandler (for output to a file) ---
        file_handler = logging.FileHandler(f"{os.path.join(self.config.output_folder_path, 'app.log')}")
        file_handler.setLevel(logging.DEBUG) # Set minimum level for the file
        file_handler.setFormatter(formatter)

        # --- Setup StreamHandler (for output to stdio/console) ---
        # By default, StreamHandler outputs to sys.stderr
        stream_handler = logging.StreamHandler(sys.stdout) # Explicitly set to stdout
        stream_handler.setLevel(logging.DEBUG) # Set minimum level for the console
        stream_handler.setFormatter(formatter)

        # 3. Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        self._logger = logger

        return self
    

    def info(self, message):
        self._logger.info(f"INFO | {message}")

    def success(self, message):
        self._logger.info(f"SUCCESS | {message}")

    def error(self, message):
        self._logger.error(f"ERROR | {message}")

    def debug(self, message):
        self._logger.debug(f"DEBUG | {message}")