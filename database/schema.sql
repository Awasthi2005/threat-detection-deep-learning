-- Real-Time Threat Detection Database Schema

CREATE DATABASE IF NOT EXISTS threat_db;
USE threat_db;

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

-- Insert sample initial data if table is empty
INSERT INTO threats (type, status, confidence, source_ip, destination_ip, protocol, timestamp)
SELECT * FROM (
    SELECT 'Normal' AS type, 'Normal' AS status, 98.5 AS confidence, '192.168.1.105' AS source_ip, '172.217.16.206' AS destination_ip, 'TCP' AS protocol, NOW() - INTERVAL 10 MINUTE UNION ALL
    SELECT 'DoS Attack' AS type, 'Critical' AS status, 94.2 AS confidence, '45.33.32.156' AS source_ip, '192.168.1.1' AS destination_ip, 'UDP' AS protocol, NOW() - INTERVAL 8 MINUTE UNION ALL
    SELECT 'Probe' AS type, 'Warning' AS status, 88.7 AS confidence, '185.220.101.5' AS source_ip, '192.168.1.105' AS destination_ip, 'TCP' AS protocol, NOW() - INTERVAL 5 MINUTE UNION ALL
    SELECT 'R2L Attack' AS type, 'Critical' AS status, 91.0 AS confidence, '198.51.100.24' AS source_ip, '192.168.1.105' AS destination_ip, 'ICMP' AS protocol, NOW() - INTERVAL 2 MINUTE UNION ALL
    SELECT 'U2R Attack' AS type, 'Critical' AS status, 96.8 AS confidence, '192.168.1.105' AS source_ip, '127.0.0.1' AS destination_ip, 'TCP' AS protocol, NOW()
) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM threats LIMIT 1);
