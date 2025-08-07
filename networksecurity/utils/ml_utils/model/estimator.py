from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME

import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkModel:
    def __init__(self, model, preprocessor):
        
        """
        model: Trained model object
        preprocessor: Preprocessing object (e.g., scaler, encoder)
        """
        try:
            self.model = model
            self.preprocessor = preprocessor
        except Exception as e:
            logging.error(f"Error initializing NetworkModel: {e}")
            raise NetworkSecurityException(e, sys)
        
    def predict(self, X):
        try:
            x_transform = self.preprocessor.transform(X)
            y_hat = self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
