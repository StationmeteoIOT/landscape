import json
import socket
import network
import binascii
import hashlib
from machine import Pin
from time import sleep

class WebSocket:
    def __init__(self, port=80):
        self.port = port
        self.socket = None
        self.clients = set()
        
        # Configuration du point d'accès WiFi
        self.ssid = 'PicoBME280'
        self.password = '12345678'
        
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(essid=self.ssid, password=self.password)
        self.ap.active(True)
        
        while not self.ap.active():
            pass
        
        print(f'Point d\'accès créé: {self.ssid}')
        print(f'Adresse IP: {self.ap.ifconfig()[0]}')

    def create_handshake_response(self, key):
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        hash = hashlib.sha1((key + GUID).encode()).digest()
        response_key = binascii.b2a_base64(hash).decode().strip()
        return (
            b"HTTP/1.1 101 Switching Protocols\r\n"
            b"Upgrade: websocket\r\n"
            b"Connection: Upgrade\r\n"
            b"Sec-WebSocket-Accept: " + response_key.encode() + b"\r\n\r\n"
        )

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)
        self.socket.setblocking(False)
        print(f'WebSocket en écoute sur le port {self.port}')

    def handle_connections(self):
        if self.socket is None:
            return
            
        try:
            conn, addr = self.socket.accept()
            conn.setblocking(True)
            
            # Lecture de l'en-tête HTTP
            header = conn.recv(1024).decode()
            
            # Extraction de la clé WebSocket
            for line in header.split('\n'):
                if "Sec-WebSocket-Key" in line:
                    key = line.split(": ")[1].strip()
                    break
            
            # Envoi de la réponse handshake
            response = self.create_handshake_response(key)
            conn.send(response)
            
            self.clients.add(conn)
            print(f'Nouveau client connecté: {addr}')
            
        except Exception as e:
            pass

    def create_websocket_frame(self, data):
        # Création d'une trame WebSocket simple (non masquée)
        message = json.dumps(data).encode()
        length = len(message)
        
        # Trame de base avec FIN=1 et opcode=1 (text)
        frame = bytearray([0b10000001])
        
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(127)
            frame.extend(length.to_bytes(8, 'big'))
            
        frame.extend(message)
        return frame

    def broadcast(self, data):
        frame = self.create_websocket_frame(data)
        disconnected = set()
        
        for client in self.clients:
            try:
                client.send(frame)
            except Exception as e:
                disconnected.add(client)
                try:
                    client.close()
                except:
                    pass
        
        self.clients -= disconnected