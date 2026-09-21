import sqlite3
import os
import datetime
from config import Config

# Global database status flag
DB_TYPE = "sqlite"

def get_mysql_connection():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return conn, "mysql"
    except Exception as e:
        return None, f"mysql_error: {str(e)}"

def get_sqlite_connection():
    os.makedirs(Config.SQLITE_DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(Config.SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global DB_TYPE
    # First attempt MySQL connection
    conn, status = get_mysql_connection()
    if conn:
        DB_TYPE = "mysql"
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                status VARCHAR(30) NOT NULL,
                confidence FLOAT NOT NULL,
                source_ip VARCHAR(45) NOT NULL,
                destination_ip VARCHAR(45) NOT NULL,
                protocol VARCHAR(20) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("[DB] Successfully connected to MySQL database 'threat_db'.")
        return "mysql"
    else:
        DB_TYPE = "sqlite"
        print(f"[DB] MySQL unavailable ({status}). Initializing embedded SQLite database fallback.")
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                source_ip TEXT NOT NULL,
                destination_ip TEXT NOT NULL,
                protocol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Check if table has initial data
        cursor.execute("SELECT COUNT(*) FROM threats")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.datetime.now()
            sample_records = [
                ('Normal', 'Normal', 98.5, '192.168.1.105', '172.217.16.206', 'TCP', (now - datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')),
                ('DoS Attack', 'Critical', 94.2, '45.33.32.156', '192.168.1.1', 'UDP', (now - datetime.timedelta(minutes=8)).strftime('%Y-%m-%d %H:%M:%S')),
                ('Probe', 'Warning', 88.7, '185.220.101.5', '192.168.1.105', 'TCP', (now - datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')),
                ('R2L Attack', 'Critical', 91.0, '198.51.100.24', '192.168.1.105', 'ICMP', (now - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')),
                ('U2R Attack', 'Critical', 96.8, '192.168.1.105', '127.0.0.1', 'TCP', now.strftime('%Y-%m-%d %H:%M:%S'))
            ]
            cursor.executemany("""
                INSERT INTO threats (type, status, confidence, source_ip, destination_ip, protocol, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_records)
            conn.commit()
            
        cursor.close()
        conn.close()
        print("[DB] SQLite database fallback ready.")
        return "sqlite"

def save_threat(threat_type, status, confidence, source_ip="192.168.1.100", destination_ip="10.0.0.1", protocol="TCP"):
    global DB_TYPE
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if DB_TYPE == "mysql":
        try:
            conn, _ = get_mysql_connection()
            if conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO threats (type, status, confidence, source_ip, destination_ip, protocol, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (threat_type, status, float(confidence), source_ip, destination_ip, protocol, ts))
                conn.commit()
                inserted_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return inserted_id
        except Exception as e:
            print(f"[DB Error] MySQL insert error: {e}. Falling back to SQLite.")
            DB_TYPE = "sqlite"

    # SQLite fallback
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO threats (type, status, confidence, source_ip, destination_ip, protocol, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (threat_type, status, float(confidence), source_ip, destination_ip, protocol, ts))
        conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return inserted_id
    except Exception as e:
        print(f"[DB Error] Failed to save threat to SQLite: {e}")
        return None

def fetch_threats(limit=50, threat_type=None, status=None, search=None):
    global DB_TYPE
    
    if DB_TYPE == "mysql":
        try:
            conn, _ = get_mysql_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT id, type, status, confidence, source_ip, destination_ip, protocol, DATE_FORMAT(timestamp, '%Y-%m-%d') as date, DATE_FORMAT(timestamp, '%H:%i:%s') as time FROM threats WHERE 1=1"
                params = []
                if threat_type and threat_type != 'all':
                    query += " AND type = %s"
                    params.append(threat_type)
                if status and status != 'all':
                    query += " AND status = %s"
                    params.append(status)
                if search:
                    query += " AND (type LIKE %s OR source_ip LIKE %s OR destination_ip LIKE %s)"
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])
                    
                query += " ORDER BY id DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                return results
        except Exception as e:
            print(f"[DB Error] MySQL query failed: {e}. Switching to SQLite.")
            DB_TYPE = "sqlite"
            
    # SQLite fallback query
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        query = "SELECT id, type, status, confidence, source_ip, destination_ip, protocol, strftime('%Y-%m-%d', timestamp) as date, strftime('%H:%M:%S', timestamp) as time FROM threats WHERE 1=1"
        params = []
        if threat_type and threat_type != 'all':
            query += " AND type = ?"
            params.append(threat_type)
        if status and status != 'all':
            query += " AND status = ?"
            params.append(status)
        if search:
            query += " AND (type LIKE ? OR source_ip LIKE ? OR destination_ip LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "type": r[1],
                "status": r[2],
                "confidence": r[3],
                "source_ip": r[4],
                "destination_ip": r[5],
                "protocol": r[6],
                "date": r[7] if r[7] else "N/A",
                "time": r[8] if r[8] else "N/A"
            })
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"[DB Error] SQLite query error: {e}")
        return []

def get_stats():
    threats = fetch_threats(limit=500)
    total_records = len(threats)
    normal_count = sum(1 for t in threats if t['type'] == 'Normal')
    dos_count = sum(1 for t in threats if t['type'] == 'DoS Attack')
    probe_count = sum(1 for t in threats if t['type'] == 'Probe')
    r2l_count = sum(1 for t in threats if t['type'] == 'R2L Attack')
    u2r_count = sum(1 for t in threats if t['type'] == 'U2R Attack')
    attack_count = total_records - normal_count
    
    return {
        "total_monitored": total_records,
        "total_threats": attack_count,
        "normal_count": normal_count,
        "attack_count": attack_count,
        "class_breakdown": {
            "Normal": normal_count,
            "DoS Attack": dos_count,
            "Probe": probe_count,
            "R2L Attack": r2l_count,
            "U2R Attack": u2r_count
        },
        "db_type": DB_TYPE
    }
