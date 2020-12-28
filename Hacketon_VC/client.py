import time
from socket import *
from threading import Timer
from threading import Thread
from pynput.keyboard import Listener
import keyboard
from tkinter import *



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
            m, addr = s.recvfrom(1024)
            cookie = m[:10]
            type = m[10:13]
            server_port = m[13:]
            if cookie == b'0xfeedbeef' and type == b'0x2':
                b_m = False
        self.connect_to_server(server_port, addr[0])

    def connect_to_server(self, server_port, server_addr):
        # serverName = 'localhost'
        serverName = server_addr
        serverPort = int(server_port)
        # clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((serverName, serverPort))
        self.clientSocket.send(self.team_name.encode('utf-8'))
        #responed = self.clientSocket.recv(1024)
        m = "Received offer from " + str(serverName) + ", attempting to connect..."
        print(m)
        self.game_mode()

    def time_out(self):
        self.stop_play = True
        self.clientSocket.send("stop".encode('utf-8'))

    def key_press_and_send(self):
        key_press = keyboard.read_key(True)
        print("sent")
        self.clientSocket.send(key_press.encode('utf-8'))

    def game_mode(self):
        self.clientSocket.settimeout(13)
        try:
            message = self.clientSocket.recv(2048)
        except timeout:
            self.clientSocket.close()
            self.clientSocket = socket(AF_INET, SOCK_STREAM)
            self.stop_play = False
            self.broadcast_recive()
            return
        self.clientSocket.settimeout(None)
        print(message.decode('utf-8'))
        self.clientSocket.settimeout(2)
        #timer = Timer(10, self.time_out)
        #timer.start()
        lisen = Listener(on_press=self.on_press, suppress=True)

        def time_out(period_sec: int):
            time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
            lisen.stop()
            self.stop_play = True
            print("stop")
            try:
                self.clientSocket.send("stop".encode('utf-8'))
            except:
                return

        Thread(target=time_out, args=(10.0,)).start()
        lisen.start()

        """with Listener(on_press=self.on_press, suppress=True) as ls:
            def time_out(period_sec: int):
                time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
                ls.stop()
                self.stop_play = True
                print("stop")
                self.clientSocket.send("stop".encode('utf-8'))

            Thread(target=time_out, args=(10.0,)).start()
            ls.join()"""
        while not self.stop_play:
            #t1 = Thread(None, self.key_press_and_send(), None)
            #t1.start()
            #t1.join(timeout=1)
            """t1 = Thread(None, self.key_press_and_send(), None)
            try:
                a = 1
                #t1.start()
                #t1.join(timeout=1)
                #key_press = keyboard.read_key(True)
                #self.clientSocket.send(key_press.encode('utf-8'))
            except :
                print("t o")
                if self.stop_play:
                    self.clientSocket.send("stop".encode('utf-8'))
                continue"""
        try:
            message = self.clientSocket.recv(2048)
            print(message.decode('utf-8'))
        except:
            a = 1
        self.clientSocket.close()
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.stop_play = False
        self.broadcast_recive()

    def on_press(self, key):  # The function that's called when a key is pressed
        if not self.stop_play:
            try:
                self.clientSocket.send(format(key).encode('utf-8'))
            except:
                return

    def on_release(self, key):  # The function that's called when a key is released
        a = 1
