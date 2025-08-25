import socket
import json
import time
import threading

from app.config.settings import settings

class MainServerConnection:
    def __init__(self):
        self.host = settings.MAIN_SERVER_HOST
        self.port = int(settings.MAIN_SERVER_PORT)
        self.socket = None
        self.running = False
        self.last_data_sent = time.time()
        self.heartbeat_interval = 5
        self.heartbeat_timer = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to main server at {self.host}:{self.port}")
            self.running = True
            self.start_heartbeat_timer()
        except Exception as e:
            print(f"Error connecting to main server: {e}")

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
            print("Disconnected from main server")
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

    def send_data(self, data):
        try:
            while not self.running:
                self.connect()

            message = json.dumps(data)
            message_encoded = message.encode('utf-8')
            message_ecapsulated = b"\xff" + message_encoded + b"\xfe"
            self.socket.sendall(message_ecapsulated)
            print(f"Message Sent!\nSTRING: {message}\nENCODED: {message_ecapsulated}")
            self.reset_heartbeat_timer()
        except Exception as e:
            print(f"Error sending data: {e}")

    def start_heartbeat_timer(self):
        self.heartbeat_timer = threading.Timer(self.heartbeat_interval, self.send_heartbeat)
        self.heartbeat_timer.daemon = True
        self.heartbeat_timer.start()

    def reset_heartbeat_timer(self):
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.start_heartbeat_timer()

    def send_heartbeat(self):
        if self.running:
            heartbeat_data = {"message_type": "heartbeat"}
            self.send_data(heartbeat_data)