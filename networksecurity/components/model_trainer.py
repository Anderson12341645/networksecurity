import os
import sys
import joblib
import warnings
import logging  # Added logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
import mlflow
import dagshub

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

class ModelTrainer:
    def __init__(self, 
                 model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logger.info("ModelTrainer initialized")
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise NetworkSecurityException(e, sys.exc_info())
        
    def track_mlflow(self, model, classification_metric):
        """Track the model and metrics using MLflow."""
        try:
            logger.info("Initializing MLflow tracking...")
            # Initialize DagsHub with token
            dagshub.init(
                repo_owner='Anderson12341645',
                repo_name='networksecurity',
                mlflow=True
            )
            
            if 'DAGSHUB_TOKEN' in os.environ:
                dagshub.auth.add_app_token(os.environ['DAGSHUB_TOKEN'])
                logger.info("DagsHub authentication successful")
            else:
                logger.warning("DAGSHUB_TOKEN not found, using anonymous access")
            
            with mlflow.start_run():
                f1_score = classification_metric.f1_score
                precision_score = classification_metric.precision_score
                recall_score = classification_metric.recall_score
                
                mlflow.log_metric("f1_score", f1_score)
                mlflow.log_metric("precision_score", precision_score)
                mlflow.log_metric("recall_score", recall_score)
                
                # Save model locally
                model_path = "model.pkl"
                joblib.dump(model, model_path)
                
                # Log as artifact
                mlflow.log_artifact(model_path, "model")
                
                # Remove temporary file
                if os.path.exists(model_path):
                    os.remove(model_path)
                logger.info("MLflow tracking complete")
        except Exception as e:
            logger.error(f"MLflow tracking failed: {str(e)}")
            # Continue without failing the whole process
    
    def train_model(self, X_train, y_train, X_test, y_test):
        try:
            logger.info("Starting model training...")
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boost": GradientBoostingClassifier(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
                "Logistic Regression": LogisticRegression(verbose=1)
            }

            # ... rest of your model training code remains the same ...
            # Only added logging at key steps
            
            logger.info("Model training completed successfully")
            return model_trainer_artifact
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise NetworkSecurityException(e, sys.exc_info())

    # ... rest of your class remains the same with added logging ...