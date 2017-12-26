
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
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

queue = Queue()

queue.put(1)
queue.put(2)
queue.put(3)
print(queue.queue)
print(queue.get())
print(queue.get())
print(queue.get())
#야호
