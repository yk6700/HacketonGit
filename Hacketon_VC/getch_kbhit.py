import sys, termios, atexit
from select import select

class getch_kbhit:
    fd = sys.stdin.fileno()
    new_term = termios.tcgetattr(fd)
    old_term = termios.tcgetattr(fd)

    # new terminal setting unbuffered
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)

    # switch to normal terminal
    def set_normal_term(self):
        termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

    # switch to unbuffered terminal
    def set_curses_term(self):
        termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

    def putch(self, ch):
        sys.stdout.write(ch)

    def getch(self):
        return sys.stdin.read(1)

    def getche(self):
        ch = getch()
        putch(ch)
        return ch

    def kbhit(self):
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr != []
