from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    """
    Data class for storing the artifact of data ingestion.
    """
    trained_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifact:
    """
    Data class for storing the artifact of data validation.
    """
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str