import time
from socket import *
from threading import Timer
from threading import Thread
import msvcrt
import struct


class client:
    def __init__(self, team_name="IsYk\n"):
        self.team_name = team_name
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.stop_play = False

    def broadcast_recive(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(('', 13117))
        msg = "Client started, listening for offer requests..."
        print(msg)
        b_m = True
        while b_m:
            m_pack, addr = s.recvfrom(1024)
            m = struct.unpack('IbH', m_pack)
            cookie = hex(m[0])
            m_type = hex(m[1])
            server_port = m[2]
            if cookie == hex(0xfeedbeef) and m_type == hex(0x2):
                b_m = False
        self.connect_to_server(server_port, addr[0])

    def connect_to_server(self, server_port, server_addr):
        # serverName = 'localhost'
        serverName = server_addr
        serverPort = int(server_port)
        self.clientSocket.connect((serverName, serverPort))
        self.clientSocket.send(self.team_name.encode())
        m = "Received offer from " + str(serverName) + ", attempting to connect..."
        print(m)
        self.game_mode()

    def time_out(self):
        self.stop_play = True
        self.clientSocket.send("stop".encode())

    def key_press_and_send(self):
        key_press = msvcrt.getch()
        #key_press = keyboard.read_key(True)
        print("sent")
        self.clientSocket.send(key_press.encode())

    def game_mode(self):
        self.clientSocket.settimeout(13)
        try:
            message = self.clientSocket.recv(2048)
            if not message:
                self.clientSocket.close()
                self.clientSocket = socket(AF_INET, SOCK_STREAM)
                self.stop_play = False
                self.broadcast_recive()
        except timeout:
            self.clientSocket.close()
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.stop_play = False
            self.broadcast_recive()
            return
        self.clientSocket.settimeout(None)
        print(message.decode())
        timer = Timer(10, self.time_out)
        timer.start()

        while not self.stop_play:
            if msvcrt.kbhit():
                self.clientSocket.sendall(msvcrt.getch())
        self.clientSocket.settimeout(5)
        try:
            message = self.clientSocket.recv(2048)
            if not message:
                self.clientSocket.close()
                self.clientSocket = socket(AF_INET, SOCK_STREAM)
                self.stop_play = False
                self.broadcast_recive()
            print(message.decode())
        except timeout:
            a = 1
        self.clientSocket.settimeout(None)
        self.clientSocket.close()
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.stop_play = False
        self.broadcast_recive()

