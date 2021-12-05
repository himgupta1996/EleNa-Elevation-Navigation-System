import logging

# Create a custom logger
class Logger(object):
    def __init__(self, file_path):
        self.file_path = file_path
        pass

    def get_logger(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.logger = logging.getLogger(__name__)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(self.file_path)
        c_handler.setLevel(logging.DEBUG)
        f_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

        return self.logger