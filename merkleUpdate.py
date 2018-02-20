#-*- coding: utf-8 -*-
import threading
import os
import sys
from datetime import datetime
import time
import subprocess
import sqlite3



conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('DELETE FROM Camera')
cur.execute('DELETE FROM Camera1')
cur.execute('DELETE FROM Camera2')
cur.execute('DELETE FROM Camera3')
conn.commit()

dic = {}
ipfsAdd = subprocess.check_output('/usr/local/bin/ipfs add -r --silent rootDir', stderr=subprocess.STDOUT, shell=True)
name = ipfsAdd.decode().strip()
temp = name.replace('added ', '').split('\n')
print(temp)
