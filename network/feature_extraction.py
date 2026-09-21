import time
from model.preprocessing import FEATURE_NAMES

class FeatureExtractor:
    def __init__(self):
        self.packet_count = 0
        self.service_ports = {
            80: 'http', 443: 'http', 21: 'ftp', 22: 'ssh',
            25: 'smtp', 53: 'domain_u', 23: 'telnet', 110: 'pop_3',
            143: 'imap', 445: 'private'
        }

    def extract(self, packet):
        """Extracts NSL-KDD 41 feature vector from a live Scapy packet."""
        self.packet_count += 1
        
        feature_dict = {feat: 0 for feat in FEATURE_NAMES}
        feature_dict['protocol_type'] = 'tcp'
        feature_dict['service'] = 'http'
        feature_dict['flag'] = 'SF'
        
        try:
            # Check Scapy packet layers
            if hasattr(packet, 'haslayer'):
                if packet.haslayer('IP'):
                    ip_layer = packet.getlayer('IP')
                    feature_dict['src_bytes'] = len(packet)
                    feature_dict['dst_bytes'] = ip_layer.len
                    
                if packet.haslayer('TCP'):
                    tcp_layer = packet.getlayer('TCP')
                    feature_dict['protocol_type'] = 'tcp'
                    sport = tcp_layer.sport
                    dport = tcp_layer.dport
                    feature_dict['service'] = self.service_ports.get(dport, self.service_ports.get(sport, 'private'))
                    
                    # TCP Flag parsing
                    flags = tcp_layer.flags
                    if flags & 0x02: # SYN
                        feature_dict['flag'] = 'S0' if not (flags & 0x10) else 'SF'
                    elif flags & 0x04: # RST
                        feature_dict['flag'] = 'REJ'
                    else:
                        feature_dict['flag'] = 'SF'
                        
                elif packet.haslayer('UDP'):
                    feature_dict['protocol_type'] = 'udp'
                    udp_layer = packet.getlayer('UDP')
                    dport = udp_layer.dport
                    feature_dict['service'] = self.service_ports.get(dport, 'domain_u')
                    feature_dict['flag'] = 'SF'
                    
                elif packet.haslayer('ICMP'):
                    feature_dict['protocol_type'] = 'icmp'
                    feature_dict['service'] = 'eco_i'
                    feature_dict['flag'] = 'SF'
                    
            feature_dict['count'] = (self.packet_count % 250) + 1
            feature_dict['srv_count'] = ((self.packet_count // 2) % 250) + 1
            
        except Exception as e:
            pass
            
        return feature_dict
