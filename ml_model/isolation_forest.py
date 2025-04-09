import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import json
from typing import List, Dict, Tuple, Any, Optional

class InsiderThreatDetector:
    """
    Anomaly detection model for insider threat detection using Isolation Forest.
    """
    
    def __init__(self, 
                 contamination: float = 0.05, 
                 random_state: int = 42,
                 n_estimators: int = 100):
        """
        Initialize the insider threat detector.
        
        Args:
            contamination: Expected proportion of anomalies in the dataset
            random_state: Random seed for reproducibility
            n_estimators: Number of trees in the forest
        """
        self.contamination = contamination
        self.random_state = random_state
        self.n_estimators = n_estimators
        
        # Initialize models
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1  # Use all processors
        )
        
        # Model metadata
        self.feature_names = None
        self.categorical_features = None
        self.model_metadata = {
            "model_type": "IsolationForest",
            "contamination": contamination,
            "n_estimators": n_estimators,
            "threshold": None,  # Will be set during training
            "training_date": None,  # Will be set during training
            "feature_importance": None  # Will be set during training
        }
    
    def _preprocess_features(self, X: pd.DataFrame, is_training: bool = False) -> np.ndarray:
        """
        Preprocess features for model training/inference.
        
        Args:
            X: Features DataFrame
            is_training: Whether this is preprocessing for training
            
        Returns:
            Preprocessed numpy array
        """
        # Store feature names during training
        if is_training:
            self.feature_names = list(X.columns)
        
        # Convert to numpy array if DataFrame
        if isinstance(X, pd.DataFrame):
            X_array = X.values
        else:
            X_array = X
        
        # Apply scaling during training or inference
        if is_training:
            X_scaled = self.scaler.fit_transform(X_array)
        else:
            X_scaled = self.scaler.transform(X_array)
        
        return X_scaled
    
    def train(self, X: pd.DataFrame, y: Optional[pd.Series] = None, 
              categorical_features: List[str] = None) -> Dict[str, Any]:
        """
        Train the anomaly detection model.
        
        Args:
            X: Features DataFrame
            y: Optional labels (not used by unsupervised models but useful for evaluation)
            categorical_features: List of categorical feature names
            
        Returns:
            Dictionary with training metrics
        """
        print("Starting model training...")
        
        # Store categorical features
        self.categorical_features = categorical_features if categorical_features else []
        
        # Preprocess features
        X_preprocessed = self._preprocess_features(X, is_training=True)
        
        # Train the model
        self.model.fit(X_preprocessed)
        
        # Get anomaly scores
        anomaly_scores = -self.model.decision_function(X_preprocessed)
        predictions = self.model.predict(X_preprocessed)
        
        # Convert predictions (-1 for anomalies, 1 for normal) to binary (1 for anomalies, 0 for normal)
        predictions_binary = np.where(predictions == -1, 1, 0)
        
        # Update model metadata
        from datetime import datetime
        self.model_metadata["training_date"] = datetime.now().isoformat()
        self.model_metadata["num_features"] = X.shape[1]
        self.model_metadata["feature_names"] = self.feature_names
        
        # If we have ground truth labels, calculate evaluation metrics
        results = {
            "num_samples": len(X),
            "num_features": X.shape[1],
            "anomaly_ratio": sum(predictions_binary) / len(predictions_binary),
        }
        
        if y is not None:
            from sklearn.metrics import confusion_matrix, classification_report
            
            # Calculate metrics
            cm = confusion_matrix(y, predictions_binary)
            report = classification_report(y, predictions_binary, output_dict=True)
            
            # Update results
            results.update({
                "accuracy": report["accuracy"],
                "precision": report["1"]["precision"],
                "recall": report["1"]["recall"],
                "f1": report["1"]["f1-score"],
                "confusion_matrix": cm.tolist(),
            })
        
        print(f"Training complete. Identified {results['anomaly_ratio']:.2%} of samples as anomalies.")
        return results
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies in new data.
        
        Args:
            X: Features DataFrame
            
        Returns:
            Tuple of (anomaly_scores, binary_predictions)
        """
        # Verify feature names match
        if self.feature_names and isinstance(X, pd.DataFrame):
            missing_cols = set(self.feature_names) - set(X.columns)
            if missing_cols:
                raise ValueError(f"Missing required features: {missing_cols}")
            
            # Ensure column order matches training
            X = X[self.feature_names]
        
        # Preprocess features
        X_preprocessed = self._preprocess_features(X)
        
        # Get anomaly scores and predictions
        anomaly_scores = -self.model.decision_function(X_preprocessed)
        predictions = self.model.predict(X_preprocessed)
        
        # Convert predictions (-1 for anomalies, 1 for normal) to binary (1 for anomalies, 0 for normal)
        predictions_binary = np.where(predictions == -1, 1, 0)
        
        return anomaly_scores, predictions_binary
    
    def explain_predictions(self, X: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Provide explanations for predictions by extracting the most anomalous features.
        
        Args:
            X: Features DataFrame
            top_n: Number of top contributing features to return
            
        Returns:
            List of dictionaries with explanations for each sample
        """
        # Verify feature names
        if not self.feature_names:
            raise ValueError("Model not trained yet. Feature names unknown.")
        
        # Ensure X has the right columns in the right order
        X = X[self.feature_names]
        
        # Get raw feature values
        feature_values = X.values
        
        # Get Z-scores of each feature
        feature_zscores = (feature_values - self.scaler.mean_) / self.scaler.scale_
        
        # Get absolute Z-scores to find most anomalous features
        abs_zscores = np.abs(feature_zscores)
        
        explanations = []
        for i in range(len(X)):
            # Get indices of top N most anomalous features
            top_feature_indices = np.argsort(abs_zscores[i])[-top_n:][::-1]
            
            # Create explanation
            explanation = {
                "top_features": [
                    {
                        "feature_name": self.feature_names[idx],
                        "feature_value": float(feature_values[i, idx]),
                        "z_score": float(feature_zscores[i, idx]),
                        "is_high": bool(feature_zscores[i, idx] > 0)
                    }
                    for idx in top_feature_indices
                ]
            }
            explanations.append(explanation)
        
        return explanations
    
    def save_model(self, model_dir: str) -> str:
        """
        Save the trained model and metadata.
        
        Args:
            model_dir: Directory to save model files
            
        Returns:
            Path to the saved model
        """
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the isolation forest model
        model_path = os.path.join(model_dir, "isolation_forest.pkl")
        joblib.dump(self.model, model_path)
        
        # Save the scaler
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        # Save model metadata
        metadata_path = os.path.join(model_dir, "model_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(self.model_metadata, f, indent=2)
        
        print(f"Model saved to {model_dir}")
        return model_path
    
    @classmethod
    def load_model(cls, model_dir: str) -> "InsiderThreatDetector":
        """
        Load a trained model from disk.
        
        Args:
            model_dir: Directory containing saved model files
            
        Returns:
            Loaded InsiderThreatDetector instance
        """
        # Load model metadata
        metadata_path = os.path.join(model_dir, "model_metadata.json")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create instance with parameters from metadata
        detector = cls(
            contamination=metadata.get("contamination", 0.05),
            n_estimators=metadata.get("n_estimators", 100)
        )
        
        # Load model and scaler
        model_path = os.path.join(model_dir, "isolation_forest.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        
        detector.model = joblib.load(model_path)
        detector.scaler = joblib.load(scaler_path)
        
        # Restore metadata
        detector.model_metadata = metadata
        detector.feature_names = metadata.get("feature_names")
        
        print(f"Model loaded from {model_dir}")
        return detector

def train_model_pipeline(input_data_path: str, model_output_dir: str) -> InsiderThreatDetector:
    """
    End-to-end model training pipeline.
    
    Args:
        input_data_path: Path to engineered features CSV
        model_output_dir: Directory to save model files
        
    Returns:
        Trained InsiderThreatDetector instance
    """
    print(f"Loading data from {input_data_path}...")
    df = pd.read_csv(input_data_path)
    
    # Check if we have labeled data
    has_labels = 'is_anomaly' in df.columns
    
    # Define feature columns to use
    # Exclude metadata, labels, and IDs
    exclude_cols = ['id', 'user_id', 'timestamp', 'ip_address', 'action', 'resource', 
                   'is_anomaly', 'anomaly_type', 'date']
    
    # Define categorical features
    categorical_features = ['day_part', 'day_of_week', 'geo_country', 'geo_city', 'geo_isp']
    categorical_features = [f for f in categorical_features if f in df.columns]
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    print(f"Using {len(feature_cols)} features for training")
    
    # Prepare data
    X = df[feature_cols]
    y = df['is_anomaly'] if has_labels else None
    
    # Initialize and train model
    detector = InsiderThreatDetector(contamination=0.05)
    results = detector.train(X, y, categorical_features=categorical_features)
    
    # Save model
    model_path = detector.save_model(model_output_dir)
    
    # Plot and save evaluation results if we have labels
    if has_labels:
        # Create evaluation directory
        eval_dir = os.path.join(model_output_dir, "evaluation")
        os.makedirs(eval_dir, exist_ok=True)
        
        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        cm = np.array(results['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Normal', 'Anomaly'],
                   yticklabels=['Normal', 'Anomaly'])
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.savefig(os.path.join(eval_dir, 'confusion_matrix.png'))
        
        # Save text report
        report_path = os.path.join(eval_dir, 'evaluation_report.txt')
        with open(report_path, 'w') as f:
            f.write("Insider Threat Detection Model Evaluation\n")
            f.write("=======================================\n\n")
            f.write(f"Model type: {detector.model_metadata['model_type']}\n")
            f.write(f"Number of samples: {results['num_samples']}\n")
            f.write(f"Anomaly ratio: {results['anomaly_ratio']:.2%}\n\n")
            f.write("Performance Metrics:\n")
            f.write(f"Accuracy: {results['accuracy']:.4f}\n")
            f.write(f"Precision: {results['precision']:.4f}\n")
            f.write(f"Recall: {results['recall']:.4f}\n")
            f.write(f"F1-score: {results['f1']:.4f}\n")
    
    print("Model training and evaluation complete.")
    return detector

if __name__ == "__main__":
    # Example usage
    input_path = '../logs/engineered_features.csv'
    model_dir = '../ml_model/trained_models'
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        print("Run feature engineering script first.")
        exit(1)
    
    # Train the model
    detector = train_model_pipeline(input_path, model_dir)