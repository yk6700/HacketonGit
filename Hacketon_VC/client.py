import time
from socket import *
from threading import Timer
from threading import Thread
import getch as msvcrt
import struct
import sys, termios, atexit
from select import select
from getch_kbhit import getch_kbhit


class client:
    def __init__(self, team_name="The Tapandegan\n"):
        self.team_name = team_name
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.stop_play = False
        self.gb = getch_kbhit()
        atexit.register(self.gb.set_normal_term)
        self.gb.set_curses_term()

    def broadcast_recive(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        try:
            s.bind(('', 13124))  # TODO change to 13117
        except:
            self.broadcast_recive()
        msg = "Client started, listening for offer requests..."
        print(msg)
        b_m = True
        while b_m:
            m_pack, addr = s.recvfrom(4096)
            print(addr)
            try:
                (cookie, m_type, server_port) = struct.unpack('IBH', m_pack)
            except:
                continue
            cookie = hex(cookie)
            m_type = hex(m_type)
            
            if cookie == hex(0xfeedbeef) and m_type == hex(0x2):
                b_m = False
        self.connect_to_server(server_port, addr[0])

    def connect_to_server(self, server_port, server_addr):
        # serverName = 'localhost'
        serverName = server_addr
        serverPort = int(server_port)
        try:
            self.clientSocket.connect((serverName, serverPort))
        except:
            self.broadcast_recive()
        self.clientSocket.send(self.team_name.encode())
        m = "Received offer from " + str(serverName) + ", attempting to connect..."
        print(m)
        self.game_mode()

    def time_out(self):
        self.stop_play = True
        try:
            self.clientSocket.send("stop".encode())
        except:
            a = 1

    """def key_press_and_send(self):
        key_press = msvcrt.getch()
        #key_press = keyboard.read_key(True)
        print("sent")
        self.clientSocket.send(key_press.encode())"""

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
            if self.gb.kbhit():
                try:
                    self.clientSocket.send((self.gb.getch()).encode())
                except BrokenPipeError:
                    timer.cancel()
                    self.clientSocket.close()
                    self.clientSocket = socket(AF_INET, SOCK_STREAM)
                    self.stop_play = False
                    self.broadcast_recive()
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

