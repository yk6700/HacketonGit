from socket import *
import time
from _thread import *
from threading import Timer
import threading
import struct


class server:
    stop = False
    SERVER_TCP_PORT = 6666

    def __init__(self, host="172.1.0"):
        self.serverPort = 12000
        self.serverPortGame = 6666
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.teams = {}
        self.group1 = {}
        self.group2 = {}
        self.team_scores = {}
        self.best_team = ['', 0]
        self.keys_count = {}
        self.group1_score = 0
        self.group2_score = 0
        self.stop_play = False
        if host == '127.0.0.1':
            self.ip_host = host
        else:
            self.ip_host = host + ".69"

    def wating_for_clients(self):
        """
        docstring
        """
        #self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        try:
            self.serverSocket.bind(('', 13124))  # TODO bind ip address
        except:
            self.wating_for_clients()
        
        self.serverSocket.settimeout(1)
        ip = self.serverSocket.getsockname()[0]  # TODO bind ip address
        msg = 'Server started,listening on IP address ' + str(self.ip_host)
        message = struct.pack('IBH', 0xfeedbeef, 0x2, self.SERVER_TCP_PORT)
        count = 0
        while not self.stop:
            self.serverSocket.sendto(message, ('<broadcast>', 13124)) # TODO change to 13117
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
        try:
            serverSocket.bind(('', 0))
            (TCP_addr, self.SERVER_TCP_PORT) = serverSocket.getsockname()
            #serverSocket.bind(('', self.serverPortGame))
        except:
            serverSocket.close()
            self.connecting_clients()
        serverSocket.listen(1)
        while 1:
            connectionSocket, addr = serverSocket.accept()
            if addr:
                print(addr)
            b = True
            team_name_str = ''
            connectionSocket.settimeout(3)
            try:
                while b:
                    team_name = connectionSocket.recv(2048)
                    if not team_name:
                        continue
                    team_name_str += str(team_name.decode())
                    if team_name_str[-1] == '\n':
                        b = False
                connectionSocket.settimeout(None)
                self.teams[connectionSocket] = team_name_str
                self.team_scores[(connectionSocket,team_name_str)] = 0
            except timeout:
                connectionSocket.close()
                continue

    def welcome_message(self):
        message = "Welcome to Keyboard Spamming Battle Royale.\n"
        message += "Group 1:\n==\n"
        for team1 in self.group1.keys():
            message += str(self.group1[team1])
        message += "Group 2:\n==\n"
        for team2 in self.group2.keys():
            message += str(self.group2[team2])
        message += "Start pressing keys on your keyboard as fast as you can!!"
        return message

    def best_game_team(self):
        best_t = '\n'
        best_s = 0
        for team in self.team_scores.keys():
            if self.team_scores[team] >= best_s:
                best_s = self.team_scores[team]
                best_t = team[1]
        return best_t, best_s
    
    def max_key(self):
        best_k = ''
        best_s = 0
        for key in self.keys_count.keys():
            if self.keys_count[key] >= best_s:
                best_s = self.keys_count[key]
                best_k = key
        return best_k, best_s
    
    def end_game_message(self):
        s1 = self.group1_score
        s2 = self.group2_score
        message = "Game over!\n"
        message += "Group 1 typed in " + str(s1) + " characters. Group 2 typed in " + str(s2) + " characters.\n"
        if s1 > s2:
            message += "Group 1 wins!\n\n"
            message += "Congratulations to the winners:\n==\n"
            for team in self.group1.keys():
                message += str(self.group1[team])
        else:
            message += "Group 2 wins!\n\n"
            message += "Congratulations to the winners:\n==\n"
            for team in self.group2.keys():
                message += str(self.group2[team])
        message += '\n'
        best_t, best_s = self.best_game_team()
        tmp = "The best team that played this round with a score of " + str(best_s) + " is: " + str(best_t) 
        message += tmp
        if self.best_team[1] <= best_s:
            self.best_team[1] = best_s
            self.best_team[0] = best_t
        tmp = "The best team in history that played this gamee with a best score of " + str(self.best_team[1]) + " is : " + str(self.best_team[0]) 
        message += tmp
        best_k, best_s = self.max_key()
        tmp = "The most common Key that was pressed this round with a total amount of " + str(best_s) + " is: " + str(best_k) 
        message += tmp + '\n'
        return message
    

    def time_out(self):
        self.stop_play = True

    def threaded_client(self, connection_socket, group):
        w_message = self.welcome_message()
        connection_socket.send(w_message.encode())
        timer = Timer(10, self.time_out)
        timer.start()
        connection_socket.settimeout(11)
        while not self.stop_play:
            try:
                key_press = connection_socket.recv(1024)
                if not key_press:
                    return
                key_str = str(key_press.decode())
                if key_str == 'stop':
                    continue
                print(key_press.decode())
                self.team_scores[(connection_socket, self.teams[connection_socket])] += 1
                if key_str not in self.keys_count.keys():
                    self.keys_count[key_str] = 1
                else:
                    self.keys_count[key_str] += 1
                if group == 1:
                    self.group1_score += 1
                    print("score1 :" + str(self.group1_score))
                else:
                    self.group2_score += 1
                    print("score2 :" + str(self.group2_score))
            except ConnectionResetError:
                ip = str(self.serverSocket.getsockname()[0])
                connection_socket.connect((ip, self.serverPortGame))
        connection_socket.settimeout(None)
        end_message = self.end_game_message()
        connection_socket.send(end_message.encode())
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
                assigned_teams[team] = 1
                group_chose = 2
            else:
                self.group2[team] = self.teams[team]
                assigned_teams[team] = 2
                group_chose = 1
        threads = []
        print("exitttttt")
        for team in assigned_teams.keys():
            #start_new_thread(self.threaded_client, (team, assigned_teams[team],))
            t1 = threading.Thread(None,self.threaded_client,None,(team, assigned_teams[team]))
            threads.append(t1)
            t1.start()
        for t in threads:
            t.join()
        self.teams = {}
        self.group1 = {}
        self.group2 = {}
        self.group1_score = 0
        self.group2_score = 0
        self.keys_count = {}
        self.team_scores = {}
        self.stop = False
        self.stop_play = False
        self.serverSocket.close()
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.wating_for_clients()


