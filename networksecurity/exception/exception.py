import sys
from networksecurity.logging import logger  # Import should work after fixing logger.py

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)  # Initialize parent Exception
        self.error_message = error_message
        # Extract error details
        _, _, exc_tb = error_details.exc_info()
        self.lineno = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return "Error occurred in python script name [{0}] line number [{1}] error message [{2}]".format(
            self.file_name, self.lineno, str(self.error_message))

if __name__ == '__main__':
    try:
        logger.logging.info("Enter the try block")  # CORRECTED: Use logger.info
        a = 1/0
        print("This will not be printed",a)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e  # Preserve original exception