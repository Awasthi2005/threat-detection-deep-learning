import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from config import Config
from model.preprocessing import (
    FEATURE_NAMES, THREAT_CLASSES,
    DataPreprocessor, reshape_for_lstm
)

class ThreatPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = DataPreprocessor()
        self.metadata = {}
        self.is_ready = False
        self.load_model()

    def load_model(self):
        try:
            mlp_path = os.path.join(Config.MODEL_DIR, 'mlp_model.pkl')
            if os.path.exists(mlp_path) and self.preprocessor.load(Config.SCALER_PATH, Config.ENCODER_PATH):
                import joblib
                self.model = joblib.load(mlp_path)
                self.model_type = "mlp"
                if os.path.exists(Config.METADATA_PATH):
                    with open(Config.METADATA_PATH, 'r') as f:
                        self.metadata = json.load(f)
                self.is_ready = True
                print("[Predictor] Deep Learning MLP model & preprocessor loaded successfully.")
                return True
            elif os.path.exists(Config.MODEL_PATH) and self.preprocessor.load(Config.SCALER_PATH, Config.ENCODER_PATH):
                import tensorflow as tf
                self.model = tf.keras.models.load_model(str(Config.MODEL_PATH))
                self.model_type = "lstm"
                if os.path.exists(Config.METADATA_PATH):
                    with open(Config.METADATA_PATH, 'r') as f:
                        self.metadata = json.load(f)
                self.is_ready = True
                print("[Predictor] Deep Learning LSTM model & preprocessor loaded successfully.")
                return True
            else:
                print("[Predictor] Saved model files missing. Predictor operating in heuristic mode.")
                self.is_ready = False
                return False
        except Exception as e:
            print(f"[Predictor] Error loading model ({e}). Operating in heuristic mode.")
            self.is_ready = False
            return False

    def predict(self, feature_dict):
        """
        Accepts a dictionary of 41 feature values, preprocesses them, 
        and predicts threat category & confidence.
        """
        # Ensure all 41 feature keys exist with default values if missing
        row = {}
        for feat in FEATURE_NAMES:
            if feat in feature_dict:
                row[feat] = feature_dict[feat]
            elif feat == 'protocol_type':
                row[feat] = 'tcp'
            elif feat == 'service':
                row[feat] = 'http'
            elif feat == 'flag':
                row[feat] = 'SF'
            else:
                row[feat] = 0

        df_single = pd.DataFrame([row])

        if self.is_ready and self.model is not None:
            try:
                df_processed = self.preprocessor.transform(df_single)
                
                if getattr(self, 'model_type', 'lstm') == 'mlp':
                    probs = self.model.predict_proba(df_processed.values)[0]
                else:
                    X_lstm = reshape_for_lstm(df_processed.values)
                    probs = self.model.predict(X_lstm, verbose=0)[0]
                    
                class_idx = int(np.argmax(probs))
                confidence = float(probs[class_idx] * 100)
                threat_type = THREAT_CLASSES[class_idx]
            except Exception as e:
                print(f"[Predictor] Inference error ({e}), switching to heuristic prediction.")
                return self._heuristic_predict(row)
        else:
            return self._heuristic_predict(row)

        status = "Normal" if threat_type == "Normal" else "Warning" if threat_type == "Probe" else "Critical"
        return {
            "threat_type": threat_type,
            "confidence": round(confidence, 1),
            "status": status,
            "is_malicious": threat_type != "Normal"
        }

    def _heuristic_predict(self, row):
        """Fallback prediction when deep learning model is not yet compiled."""
        serror = float(row.get('serror_rate', 0))
        rerror = float(row.get('rerror_rate', 0))
        count = int(row.get('count', 0))
        num_failed = int(row.get('num_failed_logins', 0))
        root_shell = int(row.get('root_shell', 0))

        if count > 150 or serror > 0.7:
            threat_type = "DoS Attack"
            confidence = 94.5
            status = "Critical"
        elif rerror > 0.5 or row.get('flag') == 'REJ':
            threat_type = "Probe"
            confidence = 89.2
            status = "Warning"
        elif num_failed > 2:
            threat_type = "R2L Attack"
            confidence = 92.1
            status = "Critical"
        elif root_shell > 0 or row.get('su_attempted', 0) > 0:
            threat_type = "U2R Attack"
            confidence = 96.4
            status = "Critical"
        else:
            threat_type = "Normal"
            confidence = 98.7
            status = "Normal"

        return {
            "threat_type": threat_type,
            "confidence": confidence,
            "status": status,
            "is_malicious": threat_type != "Normal"
        }

# Global predictor singleton instance
predictor = ThreatPredictor()
