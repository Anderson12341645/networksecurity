from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    """
    Data class for storing the artifact of data ingestion.
    """
    trained_file_path: str
    test_file_path: str