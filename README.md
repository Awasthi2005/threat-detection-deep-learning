# Real-Time Threat Detection Using Deep Learning for Network Intrusion Detection

A complete, production-ready B.Tech CSE Final-Year Project implementing a **Real-Time Network Intrusion Detection System (NIDS)** powered by a **Deep Learning (LSTM)** model, **Flask REST API**, **Scapy Network Ingestion**, **MySQL Database** (with SQLite zero-downtime fallback), and a **Modern Cybersecurity Dashboard** built with HTML5, CSS3, JavaScript, and Chart.js.

---

## 📌 Project Overview

Modern network environments are subject to sophisticated Cyber Attacks. Traditional rule-based Intrusion Detection Systems fail to detect novel anomalies. This project utilizes a **Long Short-Term Memory (LSTM)** Recurrent Neural Network trained on the **NSL-KDD** benchmark dataset to classify network traffic in real time into **5 distinct threat categories**:

1. **Normal**: Standard benign network communication.
2. **DoS Attack**: Denial of Service (e.g., Neptune, Smurf, Pod, Teardrop).
3. **Probe**: Network surveillance & port scanning (e.g., Nmap, Satan, Ipsweep).
4. **R2L Attack**: Remote to Local unauthorized access (e.g., Guess Password, FTP Write).
5. **U2R Attack**: User to Root privilege escalation (e.g., Buffer Overflow, Rootkit).

---

## 🔥 Key Features

- **LSTM Deep Learning Core**: Uses sequence modelling to capture temporal pattern anomalies across 41 network traffic features.
- **Real-Time Interactive Dashboard**: Built with a sleek dark cybersecurity theme, animated status indicators, live stat counters, and dynamic Chart.js visualizations.
- **Resilient Dual Database Layer**: Connects to **MySQL** database (`threat_db`), with an automatic fallback to an embedded **SQLite** database (`database/threats.db`) so the project can be demonstrated seamlessly without a running MySQL server.
- **Hybrid Ingestion Engine**:
  - **Live Mode**: Real-time packet sniffing using **Scapy** and raw feature transformation.
  - **Simulation/Demo Mode**: Built-in mock attack generator for smooth presentation when administrative packet sniffing rights or compatible network interfaces are absent.
- **Searchable Threat Log**: Real-time searchable and filterable database view with threat class and severity status filters.

---

## 🏗️ System Architecture

```
[ Network Packets / Simulation ] 
               │
               ▼
   [ Scapy Feature Extractor ]  ──( 41 Features )──► [ Data Preprocessor ]
                                                             │
                                                             ▼
                                                    [ Keras LSTM Model ]
                                                             │
                                                             ▼
  [ MySQL / SQLite Database ] ◄──( Log Threat )─── [ Threat Predictor ]
               │                                             │
               ▼                                             ▼
  [ /api/history Endpoint ]                      [ /api/live Endpoint ]
               │                                             │
               └─────────────► [ Cyber Dashboard ] ◄─────────┘
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, Flask, Flask-CORS
- **Deep Learning & ML**: TensorFlow / Keras, Scikit-learn, Pandas, NumPy, Joblib
- **Network Ingestion**: Scapy
- **Database**: MySQL, SQLite (Fallback)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Cyber Theme), Vanilla JavaScript (ES6+), Chart.js
- **Environment**: VS Code on Windows (Port `5001`)

---

## 📂 Project Structure

```
New folder/
├── app.py                     # Main Flask web application & REST API routes
├── config.py                  # Environment & project configuration settings
├── requirements.txt           # Python dependencies
├── .env.example               # Template for environment variables
├── .env                       # Local environment variables
├── README.md                  # Comprehensive setup & project guide
│
├── model/
│   ├── train_model.py         # Script to train LSTM model & save weights
│   ├── predict.py             # Inference pipeline & model loading wrapper
│   ├── preprocessing.py       # NSL-KDD dataset encoders & scalers
│   └── saved_model/           # Directory storing trained model (.h5) & scalers (.pkl)
│
├── network/
│   ├── packet_capture.py      # Scapy live packet capture thread
│   ├── feature_extraction.py  # Maps IP/TCP packet headers to 41 NSL-KDD features
│   └── monitor.py             # Background orchestrator & attack simulator
│
├── database/
│   ├── schema.sql             # MySQL schema initialization script
│   └── db.py                  # Dual MySQL & SQLite connection manager
│
├── templates/
│   ├── login.html             # Cyberpunk styled login page
│   └── dashboard.html         # Main real-time monitoring dashboard
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom cybersecurity CSS design system
│   └── js/
│       ├── login.js           # Login authentication handler
│       └── dashboard.js       # Real-time polling & Chart.js graph rendering
│
└── data/                      # Dataset storage (KDDTrain+.txt)
```

---

## 🚀 Installation & Setup (Windows Command Line)

### Step 1: Clone / Open Project Folder
Open PowerShell or Command Prompt in VS Code:
```powershell
cd "c:\Users\SHASHANK AWASTHI\New folder"
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🗄️ Database Setup (MySQL)

1. Open your MySQL client (e.g., MySQL Workbench, phpMyAdmin, or Command Line).
2. Execute the `database/schema.sql` file:
```sql
CREATE DATABASE IF NOT EXISTS threat_db;
USE threat_db;
-- Table definitions are in database/schema.sql
```
3. Update your `.env` file with your MySQL root password:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=threat_db
```

> **Note**: If MySQL is not installed or the password is empty/incorrect, the application will automatically fall back to SQLite (`database/threats.db`) without throwing errors!

---

## 🧠 Model Training

To train the LSTM Deep Learning model on the NSL-KDD dataset:

Run the training script:
```powershell
python model/train_model.py
```

**Training Process Output:**
- Downloads or generates the NSL-KDD dataset.
- Cleans data, encodes categorical features (`protocol_type`, `service`, `flag`), and normalizes numerical columns.
- Reshapes features into 3D sequence matrices `(samples, 1, 41)`.
- Trains a 2-layer LSTM neural network with Dropout regularization.
- Displays accuracy, precision, recall, F1-score, and confusion matrix.
- Saves `lstm_model.h5`, `scaler.pkl`, `encoder.pkl`, and `model_metadata.json` under `model/saved_model/`.

---

## 💻 Running the Application

Start the Flask server on port `5001`:

```powershell
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5001
```

### Default Login Credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🎮 Presentation & Demo Modes

- **Simulation Mode (Default)**: Toggle switch on the top right nav bar is enabled (`checked`). The background monitor generates realistic network attack packets every 2 seconds to showcase real-time graph updates, alert notifications, and DB persistence.
- **Live Packet Capture Mode**: Toggle switch to disabled. Requires administrative rights and Npcap/WinPcap installed on Windows.

---

## 🔍 REST API Endpoint Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | GET | Redirects to `/login` or `/dashboard` |
| `GET /api/live` | GET | Returns latest threat prediction payload |
| `GET /api/history` | GET | Returns filterable threat logs (`?type=DoS&status=Critical&search=192`) |
| `GET /api/stats` | GET | Returns aggregate counts & class breakdown |
| `POST /api/predict` | POST | Accepts 41 feature dict, runs LSTM inference, saves to DB |
| `POST /api/mode` | POST | Toggles between Live and Simulation monitoring |

---

## ❓ Troubleshooting

1. **Port 5001 already in use**:
   Change `PORT=5001` in `.env` or kill existing process using:
   ```powershell
   Stop-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess -Force
   ```
2. **TensorFlow missing or compilation error**:
   The `predict.py` engine contains a built-in heuristic fallback mode that ensures API calls succeed even if TensorFlow is not yet compiled.
3. **Scapy Packet Sniffing permissions on Windows**:
   Install Npcap from [https://npcap.com/](https://npcap.com/) and run VS Code / Terminal as Administrator.

---

## 🔮 Future Improvements

- Add Multi-layer Perceptron (MLP) and Transformer comparison models.
- Implement Automated IP Blocking (iptables/Windows Firewall rule trigger on Critical alerts).
- Export Threat Reports to PDF / CSV formats.
