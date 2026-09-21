import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

# 41 standard NSL-KDD Feature Names
FEATURE_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
    'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
    'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
    'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate',
    'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
    'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
    'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
]

# Threat Category Mapping
THREAT_CLASSES = ['Normal', 'DoS Attack', 'Probe', 'R2L Attack', 'U2R Attack']

ATTACK_MAP = {
    'normal': 'Normal',
    
    # DoS
    'back': 'DoS Attack', 'land': 'DoS Attack', 'neptune': 'DoS Attack',
    'pod': 'DoS Attack', 'smurf': 'DoS Attack', 'teardrop': 'DoS Attack',
    'apache2': 'DoS Attack', 'udpstorm': 'DoS Attack', 'processtable': 'DoS Attack',
    'mailbomb': 'DoS Attack',
    
    # Probe
    'ipsweep': 'Probe', 'mscan': 'Probe', 'nmap': 'Probe',
    'portsweep': 'Probe', 'saint': 'Probe', 'satan': 'Probe',
    
    # R2L
    'ftp_write': 'R2L Attack', 'guess_passwd': 'R2L Attack', 'imap': 'R2L Attack',
    'multihop': 'R2L Attack', 'phf': 'R2L Attack', 'spy': 'R2L Attack',
    'warezclient': 'R2L Attack', 'warezmaster': 'R2L Attack', 'sendmail': 'R2L Attack',
    'named': 'R2L Attack', 'snmpgetattack': 'R2L Attack', 'snmpguess': 'R2L Attack',
    'xlock': 'R2L Attack', 'xsnoop': 'R2L Attack', 'httptunnel': 'R2L Attack',
    
    # U2R
    'buffer_overflow': 'U2R Attack', 'loadmodule': 'U2R Attack',
    'perl': 'U2R Attack', 'ps': 'U2R Attack', 'rootkit': 'U2R Attack',
    'sqlattack': 'U2R Attack', 'xterm': 'U2R Attack'
}

CATEGORICAL_COLS = ['protocol_type', 'service', 'flag']
NUMERICAL_COLS = [col for col in FEATURE_NAMES if col not in CATEGORICAL_COLS]

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_fitted = False

    def fit_transform(self, df):
        df_clean = df.copy()
        
        # Fit & transform categorical features
        for col in CATEGORICAL_COLS:
            le = LabelEncoder()
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
            self.label_encoders[col] = le

        # Fit & transform numerical features
        df_clean[NUMERICAL_COLS] = self.scaler.fit_transform(df_clean[NUMERICAL_COLS])
        self.is_fitted = True
        return df_clean

    def transform(self, df):
        df_clean = df.copy()
        for col in CATEGORICAL_COLS:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                # Handle unknown labels
                df_clean[col] = df_clean[col].astype(str).map(
                    lambda s: le.transform([s])[0] if s in le.classes_ else 0
                )
        if self.is_fitted:
            df_clean[NUMERICAL_COLS] = self.scaler.transform(df_clean[NUMERICAL_COLS])
        return df_clean

    def save(self, scaler_path, encoder_path):
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoders, encoder_path)

    def load(self, scaler_path, encoder_path):
        if os.path.exists(scaler_path) and os.path.exists(encoder_path):
            self.scaler = joblib.load(scaler_path)
            self.label_encoders = joblib.load(encoder_path)
            self.is_fitted = True
            return True
        return False

def reshape_for_lstm(X_data):
    """Reshapes 2D tabular features into 3D for LSTM input: (samples, timesteps=1, features)"""
    return np.reshape(X_data, (X_data.shape[0], 1, X_data.shape[1]))
