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
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler



Camerapath = '/Users/leebongho/monitoring/Camera_/'
fileLog='/Users/leebongho/monitoring/fileLog.txt'
encfileLog = '/Users/leebongho/monitoring/encfileLog.txt'
encDir = '/Users/leebongho/monitoring/encCamera_/'
metaData = '/Users/leebongho/monitoring/metaData.txt'
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()


def file_len(fname):
    i=0
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

""""""
def Camera(i) :
    os.chdir('/Users/leebongho/monitoring/Camera_')
    i=i+1
    try:
        sub = subprocess.check_output('openRTSP -D 1 -c -B 10000000 -b 10000000 -q -Q -F '+ str(i) +' -d 28800 -P 60 -t -u root kistimrc rtsp://192.168.1.54/mpeg4/media.amp', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera(i)
""""""

""""""
def insert_db(ipfsAd) :
	filename=ipfsAd.split(' ')[-1].strip()
	filehash=ipfsAd.split(' ')[-2]
	dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')
	g=geocoder.ip('me')
	date_ = str(dt)
	loca_ = str(g.latlng)
	query = 'INSERT INTO metaData(name, _hash, _date, _loca, _enc) VALUES(?, ?, ?, ?, ?)'
	cur.execute(query, (filename, filehash, date_, loca_, 'hi'))
	conn.commit()
""""""

""""""
class LogHandler(PatternMatchingEventHandler) :

	eventLog  = ""

	def __init__(self) :
		super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
		f=open(fileLog,'wr+')
		f.seek(0)
		f.truncate()
		f.close()

	def on_created(self, event):
		super(LogHandler, self).on_created(event)
		what = 'Directory' if event.is_directory else 'File'
		self.eventLog = "created, " + event.src_path
		print(self.eventLog)
		with open(fileLog, 'a') as fout :
			fout.write(self.eventLog.split('/')[-1])
			fout.write('\n')
			fout.close()

""""""



""""""
def moni() :
    pre_content = f_readInit()
    while True:
        time.sleep(5)
        if file_len(fileLog) > 1 :
            f=open(fileLog,'r')
            f_content = f.read()
            if pre_content != f_content :
                diff_content = f_content.replace(pre_content, '')
                subth = threading.Thread(target = catch_thread, args=(diff_content,))
                subth.start()
            pre_content = f_content
            f.close()

""""""


""""""
def f_readInit() :
    f = open(fileLog)
    c = f.read()
    f.close()
    return c
""""""



""""""
def catch_thread(diff_cnt) :
    with open(fileLog, 'r') as fout :
        addedData = fout.readlines()
        toAdd = addedData[-2]
        fout.close()

    AES_key = EncDec.Random.new().read(32)     #AES_key to encrypt mov
    enc_key = EncDec.rsa_enc(AES_key)          #AES_key.enc by public_key
    dec_key = EncDec.rsa_dec(enc_key)          #AES_key.dec by private_key
    in_filename = Camerapath + toAdd.strip()
    os.chdir(encDir)
    EncDec.encrypt_file(AES_key, in_filename, out_filename='output')   #encrypt mov with AES_KEY
    print 'Encrypte Done !'



""""""

if __name__ == '__main__' :
    #Camera_thread = threading.Thread(target=Camera, args=(0,))
    #Camera_thread.daemon = True
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/Users/leebongho/monitoring/Camera_', recursive=True)
    observer.start()
    #Camera_thread.start()
    time.sleep(2)
    moni()


    try :
        while True :
			time.sleep(1)
    except KeyboardInterrupt :
		observer.stop()
    observer.join()
