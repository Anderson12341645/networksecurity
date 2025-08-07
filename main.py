from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (DataIngestionConfig, 
                                                DataValidationConfig, 
                                                DataTransformationConfig,
                                                ModelTrainerConfig,  # ADDED
                                                TrainingPipelineConfig)
from networksecurity.components.model_trainer import ModelTrainer
import sys
import os

if __name__ == '__main__':
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        
        # Data Ingestion
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed successfully")
        print(dataingestionartifact) 
        
        # Data Validation
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(data_validation_config, dataingestionartifact)
        logging.info("Initiate the data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed successfully")
        
        # Data Transformation
        logging.info("Data transformation started")
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data transformation completed successfully")

        # MODEL TRAINER SECTION - FIXED
        logging.info("Model training started")
        
        # 1. Create Model Trainer Config
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=trainingpipelineconfig)
        
        # 2. Initialize Model Trainer
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )
        
        # 3. Initiate model training
        model_trainer_artifact = model_trainer.initiate_model_trainer()  # ADDED THIS CALL
        logging.info(f"Model training completed successfully: {model_trainer_artifact}")

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e