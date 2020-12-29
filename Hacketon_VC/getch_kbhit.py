import sys, termios, atexit
from select import select

class getch_kbhit:

    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)

    # switch to normal terminal
    def set_normal_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    # switch to unbuffered terminal
    def set_curses_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

    def putch(self, ch):
        sys.stdout.write(ch)

    def getch(self):
        return sys.stdin.read(1)

    def getche(self):
        ch = self.getch()
        self.putch(ch)
        return ch

    def kbhit(self):
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr != []
