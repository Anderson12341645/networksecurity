import sys
from networksecurity.logging import logger  # Import should work after fixing logger.py

# exception.py - Fixed NetworkSecurityException class
class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details):
        super().__init__(error_message)
        self.error_message = error_message
        self.error_details = error_details

    def __str__(self):
        if isinstance(self.error_details, tuple) and len(self.error_details) == 3:
            _, _, exc_tb = self.error_details
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
        else:
            file_name = "Unknown file"
            line_number = "Unknown line"
            
        return f"Error occurred in python script name [{file_name}] line number [{line_number}] error message [{self.error_message}]"