import time
from socket import *
from threading import Timer
from threading import Thread
import threading
import getch as msvcrt
import struct
import sys, termios, atexit
from select import select
from getch_kbhit import getch_kbhit


class client:

    Black = '\u001b[30m'
    Red =  '\u001b[31m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Magenta = '\u001b[35m'
    Cyan = '\u001b[36m'
    White = '\u001b[37m'
    Reset = '\u001b[0m'

    def __init__(self, team_name="The Tapandegan\n"):
        self.team_name = team_name
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.stop_play = False
        self.gb = getch_kbhit()
        atexit.register(self.gb.set_normal_term)
        self.gb.set_curses_term()

    def broadcast_recive(self): # udp reciver
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        try:
            s.bind(('', 13117))  # TODO change to 13117
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
            
            if cookie == hex(0xfeedbeef) and m_type == hex(0x2): # check for right message
                b_m = False
        self.connect_to_server(server_port, addr[0]) # connectin to tcp server

    def connect_to_server(self, server_port, server_addr): # tcp conneting
        serverName = server_addr
        serverPort = int(server_port)
        try:
            self.clientSocket.connect((serverName, serverPort)) # trying to connect to server
        except:
            self.broadcast_recive()
        self.clientSocket.send(self.team_name.encode())
        m = self.Reset + "Received offer from " + self.Magenta + str(serverName) +self.Reset + ", attempting to connect..."
        print(m)
        self.game_mode() #starting game

    def time_out(self):
        self.stop_play = True
        try:
            self.clientSocket.send("stop".encode())
        except:
            a = 1


    def game_mode(self):
        self.clientSocket.settimeout(13)
        try:
            message = self.clientSocket.recv(2048) # wating for message from server to start the game
            if not message:
                self.clientSocket.close()
                self.clientSocket = socket(AF_INET, SOCK_STREAM)
                self.stop_play = False
                self.broadcast_recive()
        except:
            self.clientSocket.close()
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.stop_play = False
            self.broadcast_recive()
            return
        self.clientSocket.settimeout(None)
        print(message.decode())
        timer = Timer(10, self.time_out)
        timer.start() # starting the timer for 10 sec game

        while not self.stop_play: #game itself
            time.sleep(0.001)
            if self.gb.kbhit():
                try:
                    self.clientSocket.send((self.gb.getch()).encode()) # detecting and sending key press
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
        self.broadcast_recive() #end game back to brodcast





class myThread2(threading.Thread):
    def __init__(self, threadID, name, counter, team="The Tapandegan\n"):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.team = team

    def run(self):
        c1 = client(self.team)
        c1.broadcast_recive()

thread2 = myThread2(2, "Thread-2", 2)
thread2.start()