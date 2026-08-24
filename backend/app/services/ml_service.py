import os
import json
import joblib
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, List

class DynamicMLP(nn.Module):
    def __init__(self, input_size: int, layers: List[int], dropout_rate: float = 0.3):
        super(DynamicMLP, self).__init__()
        modules = []
        in_dim = input_size
        
        # Build layers based on metadata specification
        for i, out_dim in enumerate(layers):
            modules.append(nn.Linear(in_dim, out_dim))
            if i < len(layers) - 1:  # Hidden layers
                modules.append(nn.ReLU())
                modules.append(nn.Dropout(dropout_rate))
            in_dim = out_dim
            
        self.network = nn.Sequential(*modules)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class MLPredictor:
    _instance = None

    def __init__(self, artifacts_dir: str = "model_artifacts"):
        self.artifacts_dir = artifacts_dir
        self.preprocessor = None
        self.metadata = None
        self.feature_names = None
        self.model = None
        self.optimal_threshold = 0.0707
        self._load_artifacts()

    def _load_artifacts(self):
        possible_paths = [
            self.artifacts_dir,
            os.path.join(os.path.dirname(__file__), "..", "..", "..", self.artifacts_dir),
            os.path.abspath(self.artifacts_dir)
        ]
        
        target_dir = None
        for p in possible_paths:
            if os.path.exists(os.path.join(p, "model_metadata.json")):
                target_dir = p
                break
                
        if not target_dir:
            raise FileNotFoundError(f"Could not find model artifacts in {possible_paths}")

        with open(os.path.join(target_dir, "model_metadata.json"), "r") as f:
            self.metadata = json.load(f)
            
        self.optimal_threshold = float(self.metadata.get("optimal_prediction_threshold", 0.0707))
        self.preprocessor = joblib.load(os.path.join(target_dir, "preprocessor.joblib"))

        with open(os.path.join(target_dir, "feature_names.json"), "r") as f:
            self.feature_names = json.load(f)

        # Dynamic MLP instantiation
        mlp_info = self.metadata.get("mlp_architecture", {})
        input_size = mlp_info.get("input_size", 24)
        layers = mlp_info.get("layers", [64, 32, 16, 1])
        dropout = mlp_info.get("dropout_rate", 0.3)

        self.model = DynamicMLP(input_size=input_size, layers=layers, dropout_rate=dropout)
        model_path = os.path.join(target_dir, "final_mlp_model.pth")
        
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.model.eval()
        else:
            raise FileNotFoundError(f"MLP weights missing at {model_path}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict recovery probability and risk category for a transaction dictionary.
        """
        df = pd.DataFrame([transaction])

        # Fill default columns expected by preprocessor if omitted
        defaults = {
            'amount': 2500.0,
            'payment_method': 'CARD',
            'failure_reason': 'TEMPORARY_FAILURE',
            'retry_count': 0,
            'hours_since_failure': 2.0,
            'previous_payments': 10,
            'previous_successes': 8,
            'previous_failures': 2,
            'customer_lifetime_value': 15000.0,
            'customer_tenure_days': 365,
            'avg_previous_amount': 2500.0,
            'payment_success_rate': 0.8,
            'days_since_last_success': 15.0,
            'failed_payment_count_30d': 1
        }

        for col, val in defaults.items():
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = val

        df_fe = df.copy()
        
        # Feature engineering
        prev_succ = float(df_fe['previous_successes'].iloc[0])
        prev_fail = float(df_fe['previous_failures'].iloc[0])
        df_fe['success_failure_ratio'] = prev_succ / (prev_fail + 1.0)
        df_fe['total_previous_transactions'] = prev_succ + prev_fail

        # Ensure correct column order expected by preprocessor
        if hasattr(self.preprocessor, 'feature_names_in_'):
            expected_cols = list(self.preprocessor.feature_names_in_)
            # Filter to columns present in expected_cols
            df_fe = df_fe[expected_cols]

        # Transform using preprocessor
        X_processed = self.preprocessor.transform(df_fe)
        X_tensor = torch.tensor(X_processed, dtype=torch.float32)

        # MLP Model Inference
        with torch.no_grad():
            logits = self.model(X_tensor)
            prob = torch.sigmoid(logits).item()

        recovery_eligible = bool(prob >= self.optimal_threshold)
        risk_category = "Recovery Likely" if recovery_eligible else "High Risk of Non-Recovery"

        # Non-causal contributing feature highlights
        contributing_features = self._explain_features(transaction, prob)

        return {
            "recovery_probability": round(prob, 4),
            "risk_category": risk_category,
            "recovery_eligible": recovery_eligible,
            "threshold": round(self.optimal_threshold, 4),
            "contributing_features": contributing_features
        }

    def _explain_features(self, txn: Dict[str, Any], prob: float) -> List[Dict[str, Any]]:
        features = []
        
        reason = str(txn.get("failure_reason", "")).upper()
        if "PERMANENT" in reason or "EXPIRED" in reason:
            features.append({
                "feature": "failure_reason",
                "value": txn.get("failure_reason"),
                "direction": "negative",
                "explanation": f"Decline reason '{txn.get('failure_reason')}' is correlated with lower historical recovery rates."
            })
        elif "INSUFFICIENT" in reason or "NETWORK" in reason or "TEMPORARY" in reason:
            features.append({
                "feature": "failure_reason",
                "value": txn.get("failure_reason"),
                "direction": "positive",
                "explanation": f"Failure reason '{txn.get('failure_reason')}' is associated with temporary resolution potential."
            })

        psr = float(txn.get("payment_success_rate", 0.8))
        if psr >= 0.75:
            features.append({
                "feature": "payment_success_rate",
                "value": f"{round(psr*100, 1)}%",
                "direction": "positive",
                "explanation": f"Strong historical payment success rate ({round(psr*100, 1)}%) correlates with higher recovery score."
            })
        else:
            features.append({
                "feature": "payment_success_rate",
                "value": f"{round(psr*100, 1)}%",
                "direction": "negative",
                "explanation": f"Lower historical payment success rate ({round(psr*100, 1)}%) is associated with higher recovery risk."
            })

        hours = float(txn.get("hours_since_failure", 1.0))
        if hours <= 24:
            features.append({
                "feature": "hours_since_failure",
                "value": f"{hours} hrs",
                "direction": "positive",
                "explanation": f"Recent failure timing ({hours} hrs ago) correlates positively with prompt recovery response."
            })
        else:
            features.append({
                "feature": "hours_since_failure",
                "value": f"{hours} hrs",
                "direction": "negative",
                "explanation": f"Extended elapsed time since failure ({hours} hrs) is correlated with reduced response probability."
            })

        retries = int(txn.get("retry_count", 0))
        if retries == 0:
            features.append({
                "feature": "retry_count",
                "value": 0,
                "direction": "positive",
                "explanation": "Zero previous recovery retries performed to date."
            })
        else:
            features.append({
                "feature": "retry_count",
                "value": retries,
                "direction": "negative",
                "explanation": f"Prior retry count ({retries}) indicates multiple previous unfulfilled attempts."
            })

        return features

# Global singleton helper
ml_predictor = MLPredictor.get_instance()
