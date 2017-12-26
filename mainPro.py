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



Camerapath = '/Users/leebongho/monitoring/Camera_/'
fileLog='/Users/leebongho/monitoring/fileLog.txt'
encfileLog = '/Users/leebongho/monitoring/encfileLog.txt'
encDir = '/Users/leebongho/monitoring/encCamera_/'
metaData = '/Users/leebongho/monitoring/metaData.txt'
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
queue = Queue()


""""""
def Camera(i) :
    os.chdir(Camerapath)
    i=i+1
    try:
        sub = subprocess.check_output('openRTSP -D 1 -c -B 10000000 -b 10000000 -q -Q -F '+ str(i) +' -d 28800 -P 60 -t -u root kistimrc rtsp://192.168.1.54/mpeg4/media.amp', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera(i)
""""""

""""""
def insert_db(ipfsAd,Enc_AES) :
	filename=ipfsAd.split(' ')[-1].strip()
	filehash=ipfsAd.split(' ')[-2]
	dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')
	g=geocoder.ip('me')
	date_ = str(dt)
	loca_ = str(g.latlng)
	query = 'INSERT INTO metaData(_name, ipfs_hash, _date, _loca, Enc_AES) VALUES(?, ?, ?, ?, ?)'
	cur.execute(query, (filename, filehash, date_, loca_, str(Enc_AES)))
	conn.commit()
""""""

class LogHandler(PatternMatchingEventHandler) :
    def __init__(self) :
        super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
        f = open(fileLog, 'wr+')
        f.seek(0)
        f.truncate()
        f.close()
    def on_created(self, event) :
        super(LogHandler, self).on_created(event)
        what = 'directory'
        self.eventLog = "created, " + event.src_path
        print(self.eventLog)
        with open(fileLog, 'a') as fout:
            fout.write(self.eventLog.split('/')[-1])
            fout.write('\n')
            fout.close()
        queue.put(self.eventLog.split('/')[-1])

""""""
def upload_thread() :

    while True:
        check = queue.queue[0]
        temp = os.path.getsize(Camerapath + check)
        time.sleep(5)
        checkSize = Camerapath + check
        if os.path.getsize(checkSize) == temp :
            toAdd = queue.get()
            print(toAdd)
            dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')
            AES_key = EncDec.Random.new().read(32)     #AES_key to encrypt mov
            enc_key = EncDec.rsa_enc(AES_key)          #AES_key.enc by public_key
            dec_key = EncDec.rsa_dec(enc_key)          #AES_key.dec by private_key
            in_filename = Camerapath + toAdd.strip()
            os.chdir(encDir)
            EncDec.encrypt_file(AES_key, in_filename, out_filename=toAdd.strip())   #encrypt mov with AES_KEY
            print('enc!!!!')
            time.sleep(2)
            ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            insert_db(ipfsAdd, enc_key)
            queue.task_done()
            print('task_done')
            time.sleep(5)
            #os.remove(Camerapath + toAdd)
            #os.remove(encDir + toAdd)

""""""

if __name__ == '__main__' :
    Camera_thread = threading.Thread(target=Camera, args=(0,))
    Camera_thread.daemon = True
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=Camerapath, recursive=True)
    observer.start()
    Camera_thread.start()
    time.sleep(2)
    upload = threading.Thread(target = upload_thread)
    upload.start()


    try :
        while True :
			time.sleep(1)
    except KeyboardInterrupt :
		observer.stop()
    observer.join()
