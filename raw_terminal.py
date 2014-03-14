
import fcntl
import os
import pty
import select
import socket
import subprocess
import termios


class RawTerminal(object):
    IFLAG_MASK = ~(termios.IGNBRK
                 | termios.BRKINT
                 | termios.PARMRK
                 | termios.ISTRIP
                 | termios.INLCR
                 | termios.IGNCR
                 | termios.ICRNL
                 | termios.IXON)
    OFLAG_MASK = ~(termios.OPOST)
    LFLAG_MASK = ~(termios.ECHO
                 | termios.ECHONL
                 | termios.ICANON
                 | termios.ISIG
                 | termios.IEXTEN)
    CFLAG_MASK = ~(termios.CSIZE
                 | termios.PARENB)

    def __init__(self, fd):
        self.fd = fd

    def start(self):
        self._attrs = termios.tcgetattr(self.fd)
        new_attrs = self._attrs[:]
        new_attrs[0] &= self.IFLAG_MASK
        new_attrs[1] &= self.OFLAG_MASK
        new_attrs[2] &= self.CFLAG_MASK
        new_attrs[2] |= termios.CS8
        new_attrs[3] &= self.LFLAG_MASK
        termios.tcsetattr(self.fd, termios.TCSANOW, new_attrs)

    def stop(self):
        termios.tcsetattr(self.fd, termios.TCSANOW, self._attrs)


def spawn(*args, **kwargs):
    master = None
    slave = None
    def pre_fn():
        os.setsid()
        os.close(master)
        fcntl.ioctl(slave, 536900705, 1)
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)
        if slave > 2:
            os.close(slave)
        #os.close(os.open(os.ttyname(1), os.O_RDWR))

    master, slave = pty.openpty()
    kwargs['preexec_fn'] = pre_fn
    try:
        proc = subprocess.Popen(*args, **kwargs)
    except Exception:
        os.close(master)
        os.close(slave)
        raise

    os.close(slave)
    return proc, master


#proc, master = spawn(['ssh', 'h'])
proc, master = spawn(['bash'])

rt = RawTerminal(0)
rt.start()
try:
    while True:
        rfds, wfds, efds = select.select([master, 0], [], [])
        if rfds:
            if rfds[0] == master:
                ch = os.read(master, 1)
                if not ch:
                    break
                os.write(1, ch)
            elif rfds[0] == 0:
                ch = os.read(0, 1)
                if ord(ch) == 0x1d:
                    break
                os.write(master, ch)
finally:
    rt.stop()
