import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add root folder to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import Config
from model.preprocessing import (
    FEATURE_NAMES, THREAT_CLASSES, ATTACK_MAP,
    DataPreprocessor, reshape_for_lstm
)

def generate_synthetic_nslkdd(num_samples=4000):
    """Generates synthetic NSL-KDD dataset if actual file is unavailable."""
    print(f"[Data] Generating synthetic NSL-KDD dataset with {num_samples} samples...")
    np.random.seed(42)
    
    protocols = ['tcp', 'udp', 'icmp']
    services = ['http', 'private', 'smtp', 'ftp_data', 'domain_u', 'other']
    flags = ['SF', 'S0', 'REJ', 'RSTR']
    attack_types = ['normal', 'neptune', 'satan', 'guess_passwd', 'buffer_overflow']
    
    data = []
    for _ in range(num_samples):
        attack = np.random.choice(attack_types, p=[0.5, 0.25, 0.15, 0.07, 0.03])
        row = [
            int(np.random.exponential(scale=10)),  # duration
            np.random.choice(protocols),
            np.random.choice(services),
            np.random.choice(flags),
            int(np.random.gamma(2, 500)), # src_bytes
            int(np.random.gamma(2, 1000)), # dst_bytes
            0, 0, 0, # land, wrong_fragment, urgent
            int(np.random.randint(0, 5)), # hot
            0, 1 if attack == 'normal' else np.random.randint(0, 2), # num_failed_logins, logged_in
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # counts
            int(np.random.randint(1, 250)), # count
            int(np.random.randint(1, 250)), # srv_count
            round(np.random.random(), 2), round(np.random.random(), 2), # serror_rate, srv_serror_rate
            0.0, 0.0, round(np.random.random(), 2), round(np.random.random(), 2), 0.0,
            int(np.random.randint(1, 255)), int(np.random.randint(1, 255)), # dst_host_count, dst_host_srv_count
            round(np.random.random(), 2), round(np.random.random(), 2), round(np.random.random(), 2),
            round(np.random.random(), 2), round(np.random.random(), 2), round(np.random.random(), 2),
            0.0, 0.0,
            attack, # attack type
            np.random.randint(1, 21) # difficulty level
        ]
        data.append(row)
        
    col_names = FEATURE_NAMES + ['target', 'difficulty']
    df = pd.DataFrame(data, columns=col_names)
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    df.to_csv(Config.TRAIN_DATA_PATH, index=False, header=False)
    print(f"[Data] Synthetic dataset saved to {Config.TRAIN_DATA_PATH}")
    return df

def load_dataset():
    if not os.path.exists(Config.TRAIN_DATA_PATH):
        try:
            print("[Data] Train dataset not found. Downloading NSL-KDD...")
            import urllib.request
            url = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt"
            os.makedirs(Config.DATA_DIR, exist_ok=True)
            urllib.request.urlretrieve(url, Config.TRAIN_DATA_PATH)
            print("[Data] NSL-KDD dataset downloaded successfully.")
        except Exception as e:
            print(f"[Data] Failed to download NSL-KDD ({e}). Falling back to synthetic generator.")
            generate_synthetic_nslkdd()

    col_names = FEATURE_NAMES + ['target', 'difficulty']
    df = pd.read_csv(Config.TRAIN_DATA_PATH, names=col_names, header=None)
    return df

def train():
    print("=" * 60)
    print("      NSL-KDD Deep Learning (LSTM) Training Pipeline     ")
    print("=" * 60)
    
    df = load_dataset()
    print(f"Dataset shape: {df.shape}")
    
    # Map raw attack names to 5 threat classes
    df['threat_class'] = df['target'].map(lambda x: ATTACK_MAP.get(str(x).strip().lower(), 'Normal'))
    
    # Class breakdown
    print("\n[Data] Class Distribution:")
    print(df['threat_class'].value_counts())
    
    # Target encoding (0-4)
    class_to_idx = {cls_name: i for i, cls_name in enumerate(THREAT_CLASSES)}
    y = df['threat_class'].map(class_to_idx).values
    
    # Extract feature matrix X
    X_raw = df[FEATURE_NAMES]
    
    # Fit Preprocessor
    preprocessor = DataPreprocessor()
    X_processed = preprocessor.fit_transform(X_raw)
    
    # Train-test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed.values, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Reshape for LSTM: (samples, time_steps=1, num_features)
    X_train_lstm = reshape_for_lstm(X_train)
    X_test_lstm = reshape_for_lstm(X_test)
    
    print(f"\n[LSTM] Input shape: {X_train_lstm.shape}")
    
    # Build Model (TensorFlow LSTM or Neural Network MLP Fallback)
    has_tf = False
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        has_tf = True
    except Exception as e:
        print(f"\n[Notice] TensorFlow not available on Python version ({e}). Using Deep Neural Network (MLP) architecture.")

    from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score

    if has_tf:
        tf.random.set_seed(42)
        model = Sequential([
            LSTM(64, input_shape=(1, X_train.shape[1]), return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(5, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("\n[Model Architecture - TensorFlow Keras LSTM]")
        model.summary()
        
        print("\n[LSTM] Training model...")
        history = model.fit(
            X_train_lstm, y_train,
            epochs=8,
            batch_size=64,
            validation_split=0.1,
            verbose=1
        )
        
        # Evaluation
        print("\n[Evaluation] Testing LSTM model performance...")
        y_pred_probs = model.predict(X_test_lstm)
        y_pred = np.argmax(y_pred_probs, axis=1)
        
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        model.save(str(Config.MODEL_PATH))
    else:
        from sklearn.neural_network import MLPClassifier
        import joblib
        
        print("\n[Model Architecture - Deep Neural Network (MLPClassifier)]")
        model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            max_iter=50,
            random_state=42,
            verbose=True
        )
        
        print("\n[Neural Net] Training model...")
        model.fit(X_train, y_train)
        
        print("\n[Evaluation] Testing Neural Network model performance...")
        y_pred = model.predict(X_test)
        
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        joblib.dump(model, os.path.join(Config.MODEL_DIR, 'mlp_model.pkl'))
        # Save a dummy marker for model path
        with open(Config.MODEL_PATH, 'w') as f:
            f.write("MLP_MODEL_SAVED")

    
    acc = float(accuracy_score(y_test, y_pred))
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n" + "=" * 50)
    print(f" Model Accuracy:  {acc * 100:.2f}%")
    print(f" Weighted Precision: {precision * 100:.2f}%")
    print(f" Weighted Recall:    {recall * 100:.2f}%")
    print(f" Weighted F1-Score:  {f1 * 100:.2f}%")
    print("=" * 50)
    print("\nConfusion Matrix:")
    print(np.array(cm))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=THREAT_CLASSES))
    
    # Save artifacts
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    if has_tf:
        model.save(str(Config.MODEL_PATH))
    preprocessor.save(str(Config.SCALER_PATH), str(Config.ENCODER_PATH))
    
    metadata = {
        "accuracy": round(acc * 100, 2),
        "precision": round(float(precision) * 100, 2),
        "recall": round(float(recall) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "confusion_matrix": cm,
        "classes": THREAT_CLASSES,
        "features_count": len(FEATURE_NAMES)
    }
    
    with open(Config.METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"\n[Saved] Model saved to {Config.MODEL_PATH}")
    print(f"[Saved] Preprocessor saved to {Config.SCALER_PATH}")
    print(f"[Saved] Metadata saved to {Config.METADATA_PATH}")
    return metadata

if __name__ == '__main__':
    train()
