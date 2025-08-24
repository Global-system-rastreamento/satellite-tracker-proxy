import socket
import json

from app.config.settings import settings

def send_dict_to_server(data):
    try:
        address = (settings.MAIN_SERVER_HOST, int(settings.MAIN_SERVER_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)

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