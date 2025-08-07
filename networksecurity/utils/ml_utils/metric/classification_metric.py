from networksecurity.entity.artifact_entity import ClassficationMetricArtifact
from networksecurity.exception.exception import NetworkSecurityException
from sklearn.metrics import f1_score, precision_score, recall_score

def get_classification_score(y_true, y_pred) -> ClassficationMetricArtifact:
    try:
        mode_f1_score = f1_score(y_true, y_pred)
        mode_precision_score = precision_score(y_true, y_pred)
        mode_recall_score = recall_score(y_true, y_pred)

        classification_metric = ClassficationMetricArtifact(
            f1_score=mode_f1_score,
            precision_score=mode_precision_score,
            recall_score=mode_recall_score)
        
        return classification_metric
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    