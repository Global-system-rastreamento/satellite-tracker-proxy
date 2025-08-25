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

        message = json.dumps(data)
        message_encoded = message.encode('utf-8')

        message_ecapsulated = b"\xff" + message_encoded + b"\xfe"

        sock.sendall(message_ecapsulated)
        print(f"Message Sent!\nSTRING: {message}\nENCODED: {message_ecapsulated}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if sock:
            sock.close()