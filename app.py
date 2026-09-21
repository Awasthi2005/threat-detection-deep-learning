import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

from config import Config
from database.db import init_db, fetch_threats, get_stats, save_threat
from model.predict import predictor
from network.monitor import monitor

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database connections (MySQL or SQLite fallback)
db_status = init_db()

# Start Network Monitor Background Worker
monitor.start(simulation_mode=Config.DEFAULT_SIMULATION_MODE)

# Helper function for session check
def is_logged_in():
    return session.get('logged_in', False)

# -------------------------------------------------------------------
# Page Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# -------------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # Default authentication logic (e.g. admin / admin123)
    if username == 'admin' and password == 'admin123':
        session['logged_in'] = True
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials. Use admin / admin123"}), 401

@app.route('/api/live', methods=['GET'])
def api_live():
    """Returns the latest real-time network threat prediction."""
    return jsonify(monitor.latest_prediction)

@app.route('/api/history', methods=['GET'])
def api_history():
    """Returns previous detected threats with optional search/type/status filters."""
    limit = int(request.args.get('limit', 50))
    threat_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()

    threats = fetch_threats(limit=limit, threat_type=threat_type, status=status, search=search)
    return jsonify(threats)

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Returns aggregated dashboard statistics."""
    stats = get_stats()
    stats['total_monitored'] += monitor.total_packets
    return jsonify(stats)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Accepts feature payload dictionary and runs LSTM threat prediction."""
    try:
        payload = request.get_json() or {}
        features = payload.get('features', payload)
        
        result = predictor.predict(features)
        
        src_ip = payload.get('source_ip', '192.168.1.50')
        dst_ip = payload.get('destination_ip', '10.0.0.5')
        proto = payload.get('protocol', 'TCP').upper()

        inserted_id = save_threat(
            threat_type=result['threat_type'],
            status=result['status'],
            confidence=result['confidence'],
            source_ip=src_ip,
            destination_ip=dst_ip,
            protocol=proto
        )
        
        result['db_id'] = inserted_id
        return jsonify({"success": True, "prediction": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/mode', methods=['POST'])
def api_mode():
    """Toggles between Live Packet Capture and Simulation Mode."""
    data = request.get_json() or {}
    simulation = data.get('simulation', True)
    monitor.set_mode(simulation)
    return jsonify({
        "success": True, 
        "simulation": monitor.simulation_mode,
        "message": "Simulation Mode enabled" if monitor.simulation_mode else "Live Sniffing Mode enabled"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("      REAL-TIME THREAT DETECTION USING DEEP LEARNING       ")
    print(f"      Server running at http://127.0.0.1:{Config.PORT}           ")
    print("=" * 60)
    app.run(host='127.0.0.1', port=Config.PORT, debug=Config.DEBUG)
