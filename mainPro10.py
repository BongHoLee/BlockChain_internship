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
from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_files
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler



Camerapath = '/home/pi/monitoring/Camera_/'                 #Camera_ 디렉토리 경로
fileLog='/home/pi/monitoring/fileLog.txt'
encfileLog = '/home/pi/monitoring/encfileLog.txt'
encDir = '/home/pi/monitoring/encCamera_/'                  #encCamera_ 디렉토리 경로
metaData = '/home/pi/monitoring/metaData.txt'
conn = sqlite3.connect('test.db', check_same_thread=False)          #sqlite3 데이터베이스 연결
cur = conn.cursor()                                                 #데이터베이스 커서 지정
queue = Queue()                                                     #이후 queue에 영상 데이터를 저장하기 위함.
queue2 = Queue()
'''
w3 = Web3(IPCProvider("/home/pi/Library/Ethereum/testnet/geth.ipc"))
w3.personal.unlockAccount(w3.eth.accounts[4], "gksmf5081", 0)

#compile
compiled_sol = compile_files(['user0.sol','UserCrud'])
contract_interface = compiled_sol['{}:{}'.format('user0.sol','UserCrud')]


contract = w3.eth.contract(abi=[{'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getUser', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])'''

"""openRTSP 프로그램 구동 스레드 메소드"""
def Camera(i) :
    os.chdir(Camerapath)    #Camera_ 디렉토리에서 해당 프로그램 실행을 위한 경로 설정
    i=i+1                   #프로세스가 원치않게 종료후 다시 실행되었을 때 영상 파일 이름을 명시하기 위한 변수
    try:
        sub = subprocess.check_output('openRTSP -D 1 -c -B 10000000 -b 10000000 -i -Q -F ' + str(i) + ' -d 28800 -P 50 rtsp://192.168.1.8:8554/unicast', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera(i)                   #원치않게 스레드가 종료되었을 때 다시 실행하기 위해서 재귀 호출
"""----------------------------"""

"""데이터베이스에 Insert 하기위한 메소드"""
def insert_db(ipfsAd,Enc_AES) :
    filename=ipfsAd.decode().split(' ')[-1].strip()         #영상 파일 이름을 저장하기 위한 변수, 공백 제거 처리
    filehash=ipfsAd.decode().split(' ')[-2]                 #영상 파일의 IPFS hash를 저장하기 위한 변수
    dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')    #영상 파일이 데이터베이스에 thread되는 시점을 명시
    g=geocoder.ip('me')                                    #현재 IP의 위치(IP camera의 위치를 대략적으로 표시하기 위함)
    date_ = str(dt)                                        #DB에 삽입하기 위해 string 형으로 변환
    loca_ = str(g.latlng)                                  #마찬가지
    query = 'INSERT INTO metaData(_name, ipfs_hash, _date, _loca, Enc_AES) VALUES(?, ?, ?, ?, ?)'
    cur.execute(query, (filename, filehash, date_, loca_, str(Enc_AES)))
    conn.commit()
    sql = 'SELECT * FROM metaData ORDER BY _id DESC LIMIT 1;'
    cur.execute(sql)
    inqueue = cur.fetchone()
    queue2.put(str(inqueue))



class LogHandler(PatternMatchingEventHandler) :        #모니터링 프로그램의 클래스
    def __init__(self) :                                #생성자 호출
        super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
        f = open(fileLog, 'w')            #해당 스레드가 실행될 때 마다 fileLog의 내용을 초기화 시켜주기 위함
        f.seek(0)
        f.truncate()
        f.close()
    def on_created(self, event) :           #created 이벤트 발생시에 수행할 작업
        super(LogHandler, self).on_created(event)
        what = 'directory'
        self.eventLog = "created, " + event.src_path
        print(self.eventLog)
        with open(fileLog, 'a') as fout:
            fout.write(self.eventLog.split('/')[-1])
            fout.write('\n')
            fout.close()
        queue.put(self.eventLog.split('/')[-1])     #중요함. 캐치한 이벤트 (생성된 파일)의 이름을 queue에 삽입

""""""
def upload_thread() :
    time.sleep(5)                           #주요 작업을 처리하는 업로드 스레드

    while True:                                 #무한 반복
        check = queue.queue[0]                  #queue에 삽입된 영상 파일의 이름을 저장하는 변수
        temp = os.path.getsize(Camerapath + check)  #파일의 size를 이용해서 영상이 다 받아졌는지 확인하기 위한 size 체크
        time.sleep(5)                               #파일의 size가 5초가 지나도 그대로이면 파일이 다 받아진것으로 판단하고 업로드 작업 수행
        checkSize = Camerapath + check
        if os.path.getsize(checkSize) == temp :
            toAdd = queue.get()     #queue에 삽입된 영상 파일을 get으로 가져온다.
            print(toAdd)
            dt = datetime.today().strftime('%Y-%m-%d|%H:%M:%S')
            AES_key = EncDec.Random.new().read(32)     #영상 파일 암호화를 위해 AES_key를 생성함
            enc_key = EncDec.rsa_enc(AES_key)          #AES_key를 public_key를 이용해서 암호화
            dec_key = EncDec.rsa_dec(enc_key)          #이건 솔직히 필요 없음. 이후 복호화 하기 위함 (private_key로 복호화)
            in_filename = Camerapath + toAdd.strip()   #암호화 할 영상 파일의 위치
            os.chdir(encDir)                           #암호화된 영상 파일이 저장될 위치, 즉 encCamera_에 저장
            EncDec.encrypt_file(AES_key, in_filename, out_filename=toAdd.strip())   #AES_key를 이용해서 영상 파일을 암호화
            print('enc!!!!')
            time.sleep(2)                               #2초간 정지 후 암호화된 영상 파일을 ipfs add
            ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            insert_db(ipfsAdd, enc_key)                 #ipfs의 hash와 암호화된 AES_key를 인자로 넘겨서 DB thread 함수 호출
            queue.task_done()                           #queue작업이 수행되었음을 알림.
            print('task_done')
            #os.remove(Camerapath + toAdd)              #업로드 수행 이후 영상 파일 제거
            #os.remove(encDir + toAdd)                  #업로드 수행 이후 암호화된 영상 파일 제거

""""""
def deploy() :
    while True :
        i = 0
        setData = queue2.get()
        tx_receipt = w3.eth.getTransactionReceipt('0xc9856c591bf46ebc96e1e8346085f3874544e6e1626cd0543d7c31a9f3b697b3')
        contract_address = tx_receipt['contractAddress']
        contract_instance = contract(contract_address)
        # Set
        tx = contract_instance.transact({"from": w3.eth.accounts[4],"gas": 500000}).insertData(str(setData))
        print('smart contract value inserted value : {} '.format(setData))
        while w3.eth.getTransactionReceipt(tx) is None :
            time.sleep(3)

        temp = contract_instance.call().getIndex()
        print('last index : {} '.format(temp))
        print('inserted value get : {} '.format(contract_instance.call().getUser(temp)))
        while temp >= i :
            print('index : {} '.format(i))
            print('all value : {} '.format(contract_instance.call().getUser(i)))
            i += 1
        queue2.task_done()
        print('deploy task done')


if __name__ == '__main__' :
    Camera_thread = threading.Thread(target=Camera, args=(0,))
    Camera_thread.daemon = True
    #deplpy_thread = threading.Thread(target = deploy)
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=Camerapath, recursive=True)
    observer.start()
    Camera_thread.start()
    time.sleep(2)
    upload = threading.Thread(target = upload_thread)
    upload.start()
    #deplpy_thread.start()


    try :
        while True :
		          time.sleep(1)
    except KeyboardInterrupt :
        observer.stop()
    observer.join()
