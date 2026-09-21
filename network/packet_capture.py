import threading
import time

class PacketSniffer:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.thread = None
        self.has_scapy = False
        self._check_scapy()

    def _check_scapy(self):
        try:
            import scapy.all as scapy
            self.scapy = scapy
            self.has_scapy = True
        except ImportError:
            self.has_scapy = False

    def start(self):
        if not self.has_scapy:
            print("[Packet Capture] Scapy is not available. Live sniffing disabled.")
            return False

        if self.is_running:
            return True

        self.is_running = True
        self.thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self.thread.start()
        print("[Packet Capture] Live packet capture thread started.")
        return True

    def stop(self):
        self.is_running = False
        print("[Packet Capture] Stopping packet capture...")

    def _sniff_loop(self):
        try:
            def packet_handler(pkt):
                if not self.is_running:
                    return
                if self.callback:
                    self.callback(pkt)

            # Attempt live sniffing
            self.scapy.sniff(prn=packet_handler, store=0, stop_filter=lambda p: not self.is_running)
        except Exception as e:
            print(f"[Packet Capture] Live packet capture exception ({e}). WinPcap/Npcap or admin rights may be missing.")
            self.is_running = False
