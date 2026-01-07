import socket
import threading

class Client(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.isConnected = False
        self.socket = None
        
    def run(self):
        pass
        
    def conn(self, address):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((address[0], address[1]))
            self.isConnected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def send(self, message):
        if self.socket and self.isConnected:
            try:
                self.socket.send(message.encode())
                return True
            except:
                return False
        return False
        
    def stop(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        self.isConnected = False
