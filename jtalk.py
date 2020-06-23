#coding: utf-8
import subprocess
from datetime import datetime

def jtalk(t):
    open_jtalk = ['open_jtalk']
    mech = ['-x', '/usr/local/Cellar/open-jtalk/1.11/dic']
    htsvoice = ['-m', '/usr/local/Cellar/open-jtalk/1.11/voice/mei/mei_normal.htsvoice']
    speed = ['-r', '1.0']
    outwav = ['-ow', 'out.wav']
    cmd = open_jtalk + mech + htsvoice + speed + outwav
    c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    c.stdin.write(t.encode())
    c.stdin.close()
    c.wait()
    aplay = ['afplay', 'out.wav']
    wr = subprocess.Popen(aplay)

def say_datetime():
    d = datetime.now()
    text = '%s月%s日、%s時%s分%s秒' % (d.month, d.day, d.hour, d.minute, d.second)
    jtalk(text)

if __name__ == '__main__':
    say_datetime()
