#-*- coding: utf-8 -*-
import threading
import os
import sys
from datetime import datetime
import time
import logging
import subprocess
import sqlite3
import geocoder
import EncDec
import updateDir
from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_files
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
Camerapath = '/Users/leebongho/monitoring/Camera_'
now = datetime.now()
temp_year = str(now.year)
temp_month = str(now.month)
temp_day = str(now.day)

day_path = temp_year+'/'+temp_month+'/'+temp_day
month_path = temp_year+'/'+temp_month
year_path = temp_year
sql = 'SELECT EXISTS (SELECT * FROM Camera1 WHERE path=?)'
day = (day_path,)
month = (month_path,)
year = (year_path,)
cur.execute(sql, day)
print(type(cur.fetchone()[0]))
