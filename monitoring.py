
import os
import sys
from datetime import datetime
import time
import logging
import subprocess
import sqlite3
import geocoder
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler




fileLog='./fileLog.txt'
metaData = './metaData.txt'
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()

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



class LogHandler(PatternMatchingEventHandler) :

	eventLog  = ""

	def __init__(self) :
		super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
		f=open(fileLog,'wr+')
		f.seek(0)
		f.truncate()
		f.close()


	def on_created(self, event):
		dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')
		g = geocoder.ip('me')
		super(LogHandler, self).on_created(event)
		what = 'Directory' if event.is_directory else 'File'
		self.eventLog = "created, " + event.src_path
		print(dt)
		with open(fileLog, 'a') as fout :
			fout.write(self.eventLog.split('/')[-1])
			fout.write('\n')
			fout.close()
		if file_len(fileLog) > 1 :
			with open(fileLog, 'r') as frd:
				toAdd = frd.readlines()
				print(toAdd[-2])
				ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ./Camera_/' + toAdd[-2], stderr=subprocess.STDOUT, shell=True)
				insert_db(ipfsAdd)
			with open(metaData, 'a') as adHash:
				adHash.write(ipfsAdd.split(' ')[-1].strip() + ' ' + ipfsAdd.split(' ')[-2] + ' ' + str(dt) + ' ' + str(g.latlng))
				adHash.write('\n')
		elif file_len(fileLog) == 1 :
			print("oneline")

		cur.execute('SELECT * FROM metaData')
		rows = cur.fetchall()
		for i in rows:
			print(i)

		#logList.append(self.eventLog)



def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


if __name__ == '__main__' :

	event_handler = LogHandler()
	#searchDirList('.','')
	observer = Observer()
	observer.schedule(event_handler, path='./Camera_', recursive=True)
	observer.start()
	try :
		while True :
			time.sleep(1)


	except KeyboardInterrupt :

		observer.stop()

	observer.join()
