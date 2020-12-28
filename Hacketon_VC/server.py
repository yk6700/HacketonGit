from socket import *
import time
from _thread import *
from threading import Timer
import threading
from struct import *


class player_thread(threading.Thread):
    def __init__(self, threadID, name, counter, connection_socket, group):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.connection = connection_socket
        self.group = group

    def run(self):
        server.threaded_client(self.connection, self.group)


class server:
    stop = False

    def __init__(self):
        self.serverPort = 12000
        self.serverPortGame = 14000
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.teams = {}
        self.group1 = {}
        self.group2 = {}
        self.group1_score = 0
        self.group2_score = 0
        self.stop_play = False

    def wating_for_clients(self):
        """
        docstring
        """
        self.serverSocket.bind(('127.0.0.1', self.serverPort))  # TODO bind ip address
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        ip = self.serverSocket.getsockname()[0]
        msg = 'Server started,listening on IP address ' + str(ip)
        message = bytearray('0xfeedbeef0x214000', 'utf-8')
        count = 0
        while not self.stop:
            self.serverSocket.sendto(message, ('<broadcast>', 13117))
            print(msg)
            time.sleep(1)
            count += 1
            if count == 10:
                self.stop = True
                break
        self.game_mode()
        pass

    def connecting_clients(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', self.serverPortGame))
        serverSocket.listen(1)
        while 1:
            connectionSocket, addr = serverSocket.accept()
            b = True
            team_name_str = ''
            connectionSocket.settimeout(5)
            try:
                while b:
                    team_name = connectionSocket.recv(2048)
                    team_name_str += str(team_name.decode())
                    if team_name_str[-1] == '\n':
                        b = False
                connectionSocket.settimeout(None)
                self.teams[connectionSocket] = team_name_str
            except timeout:
                connectionSocket.close()
                continue
            #connectionSocket.send(str("got it " + str(team_name.decode('utf-8'))).encode('utf-8'))
            # connectionSocket.close()

    def welcome_message(self):
        message = "Welcome to Keyboard Spamming Battle Royale.\n"
        message += "Group 1:\n==\n"
        for team1 in self.group1.keys():
            message += str(self.group1[team1]) + '\n'
        message += "Group 2:\n==\n"
        for team2 in self.group2.keys():
            message += str(self.group2[team2]) + '\n'
        message += "Start pressing keys on your keyboard as fast as you can!!"
        return message

    def end_game_message(self):
        s1 = self.group1_score
        s2 = self.group2_score
        message = "Game over!\n"
        message += "Group 1 typed in " + str(s1) + " characters. Group 2 typed in " + str(s2) + " characters.\n"
        if s1 > s2:
            message += "Group 1 wins!\n\n"
            message += "Congratulations to the winners:\n==\n"
            for team in self.group1.keys():
                message += self.group1[team] + '\n'
        else:
            message += "Group 2 wins!\n\n"
            message += "Congratulations to the winners:\n==\n"
            for team in self.group2.keys():
                message += self.group2[team] + '\n'
        return message

    def time_out(self):
        self.stop_play = True

    def threaded_client(self, connection_socket, group):
        w_message = self.welcome_message()
        connection_socket.send(w_message.encode('utf-8'))
        timer = Timer(10, self.time_out)
        timer.start()
        while not self.stop_play:
            try:
                key_press = connection_socket.recv(1024)
                if not key_press:
                    return
                key_str = str(key_press.decode('utf-8'))
                if key_str == 'stop':
                    continue
                print(key_press.decode('utf-8'))
                if group == 1:
                    self.group1_score += 1
                    print("score1 :" + str(self.group1_score))
                else:
                    self.group2_score += 1
                    print("score2 :" + str(self.group2_score))
            except ConnectionResetError:
                ip = str(self.serverSocket.getsockname()[0])
                connection_socket.connect((ip, self.serverPortGame))
        end_message = self.end_game_message()
        connection_socket.send(end_message.encode('utf-8'))
        # connection_socket.close()

    def game_mode(self):
        print(self.teams)
        if len(self.teams) == 0:
            self.stop = False
            self.serverSocket.close()
            self.serverSocket = socket(AF_INET, SOCK_DGRAM)
            self.wating_for_clients()
            return
        assigned_teams = {}
        group_chose = 1
        for team in self.teams.keys():
            if group_chose == 1:
                self.group1[team] = self.teams[team]
                # self.group1[team] = team
                assigned_teams[team] = 1
                group_chose = 2
            else:
                self.group2[team] = self.teams[team]
                # self.group2[team] = team
                assigned_teams[team] = 2
                group_chose = 1
        threads = []
        for team in assigned_teams.keys():
            #start_new_thread(self.threaded_client, (team, assigned_teams[team],))
            t1 = threading.Thread(None,self.threaded_client,None,(team, assigned_teams[team]))
            threads.append(t1)
            t1.start()
        for t in threads:
            t.join()
        print("finish")
        self.teams = {}
        self.group1 = {}
        self.group2 = {}
        self.group1_score = 0
        self.group2_score = 0
        self.stop = False
        self.stop_play = False
        self.serverSocket.close()
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.wating_for_clients()


