import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cyber_threat_detection_secret_key_2026')
    
    # Port
    PORT = int(os.environ.get('PORT', 5001))
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'threat_db')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # SQLite Fallback DB Path
    SQLITE_DB_PATH = BASE_DIR / 'database' / 'threats.db'
    
    # Model Paths
    MODEL_DIR = BASE_DIR / 'model' / 'saved_model'
    MODEL_PATH = MODEL_DIR / 'lstm_model.h5'
    SCALER_PATH = MODEL_DIR / 'scaler.pkl'
    ENCODER_PATH = MODEL_DIR / 'encoder.pkl'
    METADATA_PATH = MODEL_DIR / 'model_metadata.json'
    
    # Data Paths
    DATA_DIR = BASE_DIR / 'data'
    TRAIN_DATA_PATH = DATA_DIR / 'KDDTrain+.txt'
    TEST_DATA_PATH = DATA_DIR / 'KDDTest+.txt'
    
    # Default monitoring mode
    DEFAULT_SIMULATION_MODE = True
