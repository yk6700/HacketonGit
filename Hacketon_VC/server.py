from socket import *
import time
from _thread import *
from threading import Timer
import threading
import struct
from scapy.arch import get_if_addr


class server:
    stop = False
    SERVER_TCP_PORT = 6666

    Black = '\u001b[30m'
    Red =  '\u001b[31m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Magenta = '\u001b[35m'
    Cyan = '\u001b[36m'
    White = '\u001b[37m'
    Reset = '\u001b[0m'

    def __init__(self, host="172.99.0"):
        self.udp_ip = host[0:len(host)-1]+"255.255"
        print(self.udp_ip)
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

    def wating_for_clients(self): #UDP SENDER
        """
        docstring
        """
        self.serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        try:
            self.serverSocket.bind((self.ip_host, 13117))  
        except:
            self.wating_for_clients()
        
        self.serverSocket.settimeout(1)
        ip = self.serverSocket.getsockname()[0]  
        msg = self.Reset + 'Server started,listening on IP address ' + self.Green + str(self.ip_host) + self.Reset
        message = struct.pack('IbH', 0xfeedbeef, 0x2, self.SERVER_TCP_PORT)
        count = 0
        while not self.stop:
            self.serverSocket.sendto(message, (self.udp_ip, 13117)) # SEND the message
            print(msg)
            time.sleep(1)
            count += 1
            if count == 10:
                self.stop = True
                break
        self.game_mode()
        

    def connecting_clients(self): # TCP RECIVER
        serverSocket = socket(AF_INET, SOCK_STREAM)
        try:
            serverSocket.bind((self.ip_host, 0))
            (TCP_addr, self.SERVER_TCP_PORT) = serverSocket.getsockname()
        except:
            serverSocket.close()
            self.connecting_clients()
        serverSocket.listen(1)
        while 1:
            time.sleep(1)
            connectionSocket, addr = serverSocket.accept() # wating for clients to connect to tcp
            if addr:
                print(addr)
            b = True
            team_name_str = ''
            connectionSocket.settimeout(3)
            try:
                while b: # ceck if team name good
                    team_name = connectionSocket.recv(2048)
                    if not team_name:
                        continue
                    team_name_str += str(team_name.decode())
                    if team_name_str[-1] == '\n':
                        b = False
                connectionSocket.settimeout(None)
                #add team to game data structure
                self.teams[connectionSocket] = team_name_str
                self.team_scores[(connectionSocket,team_name_str)] = 0
            except timeout:
                connectionSocket.close()
                continue

    def welcome_message(self):
        message = self.Green + "Welcome to Keyboard Spamming Battle Royale.\n"
        message += self.Blue + "Group 1:\n==\n"
        for team1 in self.group1.keys():
            message += str(self.group1[team1])
        message += self.Red + "Group 2:\n==\n"
        for team2 in self.group2.keys():
            message += str(self.group2[team2])
        message += self.Green + "Start pressing keys on your keyboard as fast as you can!!"
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
        message = self.Green + "Game over!\n"
        message += "Group 1 typed in " + str(s1) + " characters. Group 2 typed in " + str(s2) + " characters.\n"
        if s1 > s2:
            message += self.Blue + "Group 1 wins!\n\n"
            message += "Congratulations to the winners:\n==\n"
            for team in self.group1.keys():
                message += str(self.group1[team])
        else:
            message += self.Red + "Group 2 wins!\n\n"
            message += self.Green + "Congratulations to the winners:\n==\n"
            for team in self.group2.keys():
                message += str(self.group2[team])
        message += '\n'
        best_t, best_s = self.best_game_team()
        tmp = self.Cyan + "The best team that played this round with a score of "+ self.Reset + str(best_s) + self.Cyan + " is: " + self.Reset + str(best_t) 
        message += tmp
        if self.best_team[1] <= best_s:
            self.best_team[1] = best_s
            self.best_team[0] = best_t
        tmp = self.Yellow + "The best team in history that played this gamee with a best score of " + self.Reset + str(self.best_team[1]) + self.Yellow + " is : " + self.Reset + str(self.best_team[0]) 
        message += tmp
        best_k, best_s = self.max_key()
        tmp = self.Magenta + "The most common Key that was pressed this round with a total amount of " + self.Reset + str(best_s) + self.Magenta + " is: " + self.Reset + str(best_k) + self.Reset
        message += tmp + '\n'
        return message
    

    def time_out(self):
        self.stop_play = True

    def threaded_client(self, connection_socket, group): # thread for each team in game
        w_message = self.welcome_message()
        connection_socket.send(w_message.encode())
        timer = Timer(10, self.time_out)
        timer.start() # start a timer for 10 sec game
        connection_socket.settimeout(11)
        while not self.stop_play: # game itself
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
            except timeout:
                continue
        connection_socket.settimeout(None)
        end_message = self.end_game_message()
        try:
            connection_socket.send(end_message.encode())
        except:
            return

    def game_mode(self): # prepering and starting the game
        print(self.teams) # teams and their sockets
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
        for team in assigned_teams.keys(): # starting the game for every team
            t1 = threading.Thread(None,self.threaded_client,None,(team, assigned_teams[team]))
            threads.append(t1)
            t1.start()
        for t in threads: # waiting for game to end
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
        self.wating_for_clients() # going back to udp sender









ip = "172.1.0"
s1 = server()

class myThread1(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s1.wating_for_clients()


class myThread3(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s1.connecting_clients()

thread1 = myThread1(1, "Thread-1", 1)
thread3 = myThread3(3, "Thread-3", 3)
thread3.start()
thread1.start()