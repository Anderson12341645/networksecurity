from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd
import os
import sys
import numpy as np
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self, data_validation_config: DataValidationConfig, data_ingestion_artifact: DataIngestionArtifact):
        try:
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            
            # Correct schema path handling
            dir_path = os.path.dirname(SCHEMA_FILE_PATH)
            file_name = os.path.basename(SCHEMA_FILE_PATH).strip()
            corrected_schema_path = os.path.join(dir_path, file_name)
            
            # Read and parse schema
            schema_content = read_yaml_file(corrected_schema_path)
            
            # Extract columns definition
            self.schema_config = schema_content['columns']
            
            # Extract numerical columns list
            self.numerical_columns = schema_content['numerical_columns']
            
            # DEBUG: Print schema info
            print(f"Schema columns: {list(self.schema_config.keys())}")
            print(f"Number of schema columns: {len(self.schema_config)}")
            print(f"Numerical columns: {self.numerical_columns}")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            # Normalize column names
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace(' ', '_')
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self.schema_config)
            actual_columns = len(dataframe.columns)
            logging.info(f"Expected columns: {number_of_columns}, Actual columns: {actual_columns}")
            
            if actual_columns == number_of_columns:
                return True
            
            # Log column name differences
            expected_cols = set(self.schema_config.keys())
            actual_cols = set(dataframe.columns)
            missing = expected_cols - actual_cols
            extra = actual_cols - expected_cols
            
            if missing:
                logging.error(f"Missing columns: {missing}")
            if extra:
                logging.error(f"Extra columns: {extra}")
                
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_numerical_columns(self, dataframe: pd.DataFrame) -> str:
        """Validate presence and data type of numerical columns"""
        errors = []
        
        # Check missing numerical columns
        missing_columns = [col for col in self.numerical_columns 
                          if col not in dataframe.columns]
        if missing_columns:
            errors.append(f"Missing numerical columns: {missing_columns}")
        
        # Check data types
        non_numeric = []
        for col in self.numerical_columns:
            if col in dataframe.columns:
                if not pd.api.types.is_numeric_dtype(dataframe[col]):
                    non_numeric.append(col)
        if non_numeric:
            errors.append(f"Non-numeric columns: {non_numeric}")
        
        return "; ".join(errors) if errors else ""

    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            
            # Only consider numerical columns for drift detection
            numeric_columns = [
                col for col in base_df.columns 
                if pd.api.types.is_numeric_dtype(base_df[col])
            ]
            
            for column in numeric_columns:
                d1 = base_df[column]
                d2 = current_df[column]
                
                # Handle NaN values
                d1 = d1.replace([np.inf, -np.inf], np.nan).dropna()
                d2 = d2.replace([np.inf, -np.inf], np.nan).dropna()
                
                # Skip empty columns
                if len(d1) == 0 or len(d2) == 0:
                    report[column] = {"status": "skipped", "reason": "empty data"}
                    continue
                
                # Perform KS test
                result = ks_2samp(d1, d2)
                drift_detected = result.pvalue <= threshold
                
                if drift_detected:
                    status = False
                
                report[column] = {
                    "p_value": float(result.pvalue),
                    "drift_status": drift_detected
                }
            
            # Save report
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            
            return status
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            error_message = ""
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # Read datasets
            train_df = DataValidation.read_data(train_file_path)
            test_df = DataValidation.read_data(test_file_path)

            # Validate column counts
            if not self.validate_number_of_columns(dataframe=train_df):
                error_message += "Train dataframe has incorrect column count\n"
            if not self.validate_number_of_columns(dataframe=test_df):
                error_message += "Test dataframe has incorrect column count\n"

            # Validate numerical columns
            train_num_error = self.validate_numerical_columns(train_df)
            if train_num_error:
                error_message += f"Train: {train_num_error}\n"
            test_num_error = self.validate_numerical_columns(test_df)
            if test_num_error:
                error_message += f"Test: {test_num_error}\n"

            # Fail early if any validation errors
            if error_message:
                raise Exception(f"Data validation failed:\n{error_message}")

            # Check dataset drift
            drift_status = self.detect_dataset_drift(
                base_df=train_df, 
                current_df=test_df
            )

            # Save validated data
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)