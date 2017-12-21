import subprocess
import threading
import time
import os
from datetime import datetime

def MyThread(i) :
    print('hi')

def mmo(a) :
    while True:
        my = threading.Thread(target = MyThread, args=(1,))
        my.start()
        print('hihi')

if __name__=='__main__' :
    hi = threading.Thread(target = mmo, args=(1,))
    hi.start()
