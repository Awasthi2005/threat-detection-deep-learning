import time
import random
import threading
import datetime
from network.feature_extraction import FeatureExtractor
from network.packet_capture import PacketSniffer
from model.predict import predictor
from database.db import save_threat, fetch_threats

class NetworkMonitor:
    def __init__(self):
        self.simulation_mode = True
        self.extractor = FeatureExtractor()
        self.latest_prediction = {
            "threat_type": "Normal",
            "confidence": 98.5,
            "status": "Normal",
            "source_ip": "192.168.1.105",
            "destination_ip": "172.217.16.206",
            "protocol": "TCP",
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "is_malicious": False
        }
        self.total_packets = 0
        self.is_running = False
        self.sim_thread = None
        self.sniffer = PacketSniffer(callback=self.handle_scapy_packet)

    def start(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        self.is_running = True

        if self.simulation_mode:
            self.sniffer.stop()
            if self.sim_thread is None or not self.sim_thread.is_alive():
                self.sim_thread = threading.Thread(target=self._simulation_loop, daemon=True)
                self.sim_thread.start()
            print("[Monitor] Simulation Mode ACTIVE.")
        else:
            started = self.sniffer.start()
            if not started:
                print("[Monitor] Live capture failed. Reverting to Simulation Mode.")
                self.simulation_mode = True
                self.sim_thread = threading.Thread(target=self._simulation_loop, daemon=True)
                self.sim_thread.start()

    def set_mode(self, simulation_mode):
        self.simulation_mode = simulation_mode
        if simulation_mode:
            self.sniffer.stop()
            if self.sim_thread is None or not self.sim_thread.is_alive():
                self.sim_thread = threading.Thread(target=self._simulation_loop, daemon=True)
                self.sim_thread.start()
            print("[Monitor] Switched to SIMULATION MODE.")
        else:
            started = self.sniffer.start()
            if not started:
                print("[Monitor] Live packet capture unavailable. Remaining in Simulation Mode.")
                self.simulation_mode = True

    def handle_scapy_packet(self, packet):
        if not self.is_running:
            return
        
        features = self.extractor.extract(packet)
        self.total_packets += 1
        
        # Predict using deep learning model
        result = predictor.predict(features)
        
        src_ip = "192.168.1.100"
        dst_ip = "10.0.0.1"
        proto = features.get('protocol_type', 'TCP').upper()
        
        if hasattr(packet, 'haslayer') and packet.haslayer('IP'):
            ip = packet.getlayer('IP')
            src_ip = ip.src
            dst_ip = ip.dst

        self._process_result(result, src_ip, dst_ip, proto)

    def _simulation_loop(self):
        print("[Monitor] Threat Simulation thread running...")
        
        mock_ips = [
            '192.168.1.105', '10.0.0.45', '172.16.0.12',
            '45.33.32.156', '185.220.101.5', '198.51.100.24', '192.168.1.1'
        ]
        mock_dsts = ['192.168.1.1', '10.0.0.1', '172.217.16.206', '127.0.0.1']
        protocols = ['TCP', 'UDP', 'ICMP']

        while self.is_running and self.simulation_mode:
            self.total_packets += random.randint(1, 5)
            
            # 70% Normal traffic, 30% Attack simulation
            dice = random.random()
            if dice < 0.70:
                threat_type = 'Normal'
                status = 'Normal'
                confidence = round(random.uniform(95.0, 99.8), 1)
                features = {'count': random.randint(1, 20), 'serror_rate': 0.0}
            elif dice < 0.85:
                threat_type = 'DoS Attack'
                status = 'Critical'
                confidence = round(random.uniform(91.0, 98.5), 1)
                features = {'count': random.randint(200, 500), 'serror_rate': 0.95}
            elif dice < 0.92:
                threat_type = 'Probe'
                status = 'Warning'
                confidence = round(random.uniform(85.0, 94.0), 1)
                features = {'rerror_rate': 0.85, 'flag': 'REJ'}
            elif dice < 0.97:
                threat_type = 'R2L Attack'
                status = 'Critical'
                confidence = round(random.uniform(88.0, 95.0), 1)
                features = {'num_failed_logins': 4}
            else:
                threat_type = 'U2R Attack'
                status = 'Critical'
                confidence = round(random.uniform(92.0, 99.0), 1)
                features = {'root_shell': 1, 'su_attempted': 1}

            # Optional double check with predictor
            pred_res = predictor.predict(features)
            if predictor.is_ready:
                threat_type = pred_res['threat_type']
                confidence = pred_res['confidence']
                status = pred_res['status']

            src = random.choice(mock_ips)
            dst = random.choice(mock_dsts)
            proto = random.choice(protocols)

            result = {
                "threat_type": threat_type,
                "confidence": confidence,
                "status": status,
                "is_malicious": threat_type != "Normal"
            }
            
            self._process_result(result, src, dst, proto)
            time.sleep(random.uniform(1.5, 3.0))

    def _process_result(self, result, src_ip, dst_ip, proto):
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.latest_prediction = {
            "threat_type": result['threat_type'],
            "confidence": result['confidence'],
            "status": result['status'],
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "protocol": proto,
            "timestamp": ts,
            "is_malicious": result['is_malicious']
        }
        
        # Log to Database
        save_threat(
            threat_type=result['threat_type'],
            status=result['status'],
            confidence=result['confidence'],
            source_ip=src_ip,
            destination_ip=dst_ip,
            protocol=proto
        )

# Global monitor instance
monitor = NetworkMonitor()
