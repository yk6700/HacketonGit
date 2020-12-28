from server import server
from client import client
import threading
import time
import keyboard
from tkinter import *


exitFlag = 0
s1 = server()

class myThread1(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s1.wating_for_clients()


class myThread2(threading.Thread):
    def __init__(self, threadID, name, counter, team):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.team = team

    def run(self):
        c1 = client(self.team)
        c1.broadcast_recive()

class myThread3(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s1.connecting_clients()


# Create new threads
thread1 = myThread1(1, "Thread-1", 1)
thread2 = myThread2(2, "Thread-2", 2, "IsYk\n")
thread4 = myThread2(4, "Thread-4", 4, "bla\n")
thread3 = myThread3(3, "Thread-3", 3)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

#print("Exiting Main Thread")