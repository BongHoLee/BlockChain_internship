
import os
import sys
import datetime
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


logList = []
dirList = []

fileobject='./fileLog.txt'

class LogHandler(PatternMatchingEventHandler) :

	eventLog  = ""

	def __init__(self) :
		super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
		f=open('./fileLog.txt','wr+')
		f.seek(0)
		f.truncate()
		f.close()

	def on_created(self, event):
		dt = datetime.datetime.now()
		super(LogHandler, self).on_created(event)
		what = 'Directory' if event.is_directory else 'File'
		self.eventLog = "created, " + event.src_path
		print(dt)
		with open('./fileLog.txt', 'a') as fout :
			fout.write(self.eventLog.split('/')[-1])
			fout.write('\n')
			fout.close()
		if file_len('./fileLog.txt') > 1 :
			with open('./fileLog.txt', 'r') as frd:
				toAdd = frd.readlines()
				print(toAdd[-2])
				ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ' + toAdd[-2], stderr=subprocess.STDOUT, shell=True)
			with open('./hash.txt', 'a') as adHash:
				adHash.write('(' + ipfsAdd.split(' ')[-1].strip() + ') (' + ipfsAdd.split(' ')[-2] + ') (' + str(dt) + ')')
				adHash.write('\n')

				# and store hash into hash.txt with date.
		elif file_len('./fileLog.txt') == 1 :
			print("oneline")

		logList.append(self.eventLog)



def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


if __name__ == '__main__' :

	event_handler = LogHandler()
	#searchDirList('.','')
	observer = Observer()
	observer.schedule(event_handler, path='.', recursive=True)
	observer.start()
	try :
		while True :
			time.sleep(1)ㅇㅇ

	except KeyboardInterrupt :

		observer.stop()

	observer.join()
