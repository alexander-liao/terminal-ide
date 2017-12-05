import sys, os, fcntl, struct, termios, random, time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen. From http://code.activestate.com/recipes/134892/"""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self.impl = _GetchUnix()
    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt
    def __call__(self):
        import msvcrt
        return chr(msvcrt.getch()[0])

class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned. The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)
    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

def getKey():
    inkey = _Getch()
    while True:
        k = inkey()
        if k != '': break
    return k

def getOption(options):
    code = 0
    while True:
        code = ord(getKey())
        if code in options: return code

def getComboOption(options):
    code = []
    while True:
        code.append(ord(getKey()))
        if code in options: return code
        if not any(options[:len(code)] == code): code = []

def draw_char(r, c, char):
    sys.stdout.write("\033[%d;%dH%s\033[1B" % (r, c, char))

def write_char(char):
    sys.stdout.write(char)

def clear():
    ROWS, COLS = size()
    sys.stdout.write("\033[1;1H" + "\n".join(" " * COLS for _ in range(ROWS)) + "\033[1;1H")

def reset():
    sys.stdout.write("\033[0m\033[40m")

def size():
    return struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))[:2]

SAVE = 0
SAVE_AS = 1
OPEN = 2
NEW = 3
CLOSE = 4
CYCLE_R = 5
CYCLE_L = 6
QUIT = 7

key_maps = {
    [19]: SAVE,
    [27, 19]: SAVE_AS,
    [15]: OPEN,
    [14]: NEW,
    [23]: CLOSE,
    [27, 91, 49, 59, 51, 67]: CYCLE_R,
    [27, 91, 49, 59, 51, 68]: CYCLE_L,
    [17]: QUIT
}

settings = { key_maps[x]: x for x in key_maps }

def program_start():
    global settings
    option = getComboOption(*[settings[x] for x in range(8)])
    print(option)

program_start()