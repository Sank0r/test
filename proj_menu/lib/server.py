import socket
import threading
import time

class Server(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = True
        self.hasConnection = False
        self.socket = None
        
    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('0.0.0.0', self.app.port))
            self.socket.listen(1)
            self.socket.settimeout(1)
            
            while self.running:
                try:
                    client, addr = self.socket.accept()
                    self.hasConnection = True
                    self.app.peerIP = addr[0]
                    self.app.peerPort = str(addr[1])
                    client.close()
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"Server error: {e}")
            
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
