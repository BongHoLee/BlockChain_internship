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



Camerapath = '/Users/leebongho/monitoring/Camera_/'                 #Camera_ directory path : To store IP Camera streaming video clip
fileLog='/Users/leebongho/monitoring/fileLog.txt'                   #filelog.txt path
encDir = '/Users/leebongho/monitoring/encCamera_/'                  #encCamera_ directory path : To store encrypted video clip
metaData = '/Users/leebongho/monitoring/metaData.txt'
conn = sqlite3.connect('test.db', check_same_thread=False)          #Connect sqlite3 DataBase
cur = conn.cursor()                                                 #DataBase cursor
insertQ = Queue()                                                     #Queue for recieve video clip file name
deployQ = Queue()                                                    #Upload metadata of clip to DB and store it in queue2 to transmit the metadata to smartcontact
daemonQueue = Queue()                                               #exception handling queue for ipfs daemon
now = datetime.now()                                                #store now datetime
uploadQ = Queue()
waitQ1 = Queue()                                #안올린거 먼저 upload Q에 다 넣을떄까지 대기
waitQ2 = Queue()                                #안올린거 다 upload Q 에 올리고 새로 생성된거 DB에 삽입할때까지 대기



rpc_url = "http://192.168.1.2:8545"                         #HTTPProvider to communication wtih Mac mini(server)'s geth
w3 = Web3(HTTPProvider(rpc_url, request_kwargs={'timeout': 500}))
contract = w3.eth.contract(abi=[{'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getData', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])


def daemon() :                      #exception handling when ipfs daemon terminates abnormally
    try:
        daemonQueue.get()           #wait for error flag(daemon quit) in the daemonQueue
        restart = subprocess.check_output('/usr/local/bin/ipfs repo fsck', stderr=subprocess.STDOUT, shell=True)
        print('daemon resart')
        redaemon = subprocess.check_output('/usr/local/bin/ipfs daemon', stderr = subprocess.STDOUT, shell=True)
    except :
        daemon()

"""openRTSP 카메라 구동 스레드"""
def Camera2(i) :
    os.chdir(Camerapath)
    i+=1
    temp = datetime.now()
    nowDatetime = temp.strftime('%Y:%m:%d:%H:%M:%S')
    try :
        sub = subprocess.check_output('openRTSP -D 3 -B 250000 -b 250000 -c -i -F bCAM-'+str(nowDatetime)+' -P 60 rtsp://192.168.1.217//stream1', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera2(i)

def Camera3(i) :
    os.chdir(Camerapath)
    i+=1
    temp = datetime.now()
    nowDatetime = temp.strftime('%Y:%m:%d:%H:%M:%S')
    try :
        sub = subprocess.check_output('openRTSP -D 3 -B 250000 -b 250000 -c -i -F cCAM-'+str(nowDatetime)+' -P 60 rtsp://192.168.1.18:8554/unicast', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera3(i)

def Camera(i) :
    os.chdir(Camerapath)    #Set working directory to Camera_ directory (to store video clip)
    i+=1                   #variable to set restart count about openRTSP
    temp = datetime.now()
    nowDatetime = temp.strftime('%Y:%m:%d:%H:%M:%S')    #clip name
    try:
        sub = subprocess.check_output('openRTSP -D 3 -B 250000 -b 250000 -c -i -F aCAM-'+str(nowDatetime)+' -P 60 -u admin admin rtsp://192.168.1.10/11', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera(i)                   #when thread terminates abnormally, restart

"""데이터베이스에 Insert 하기위한 스레드"""
def insert_db() :
    wait = waitQ1.get()                             #inter_thread가 ready=0인 clip들을 uploadQ에 다 넣을떄까지 대기
    while True :
        name = insertQ.get()                                #새로 생성된 clip들의 이름을 가져와서 insert
        print('basic insert start')
        ctime = os.path.getctime(Camerapath + name)     #To insert create date of clip
        dt = datetime.fromtimestamp(ctime)                  #To insert create date of clip
        g = geocoder.ip('me')                               #To insert location of clip
        date = str(dt)
        loca = str(g.latlng)
        ready_flag = 0
        query = 'INSERT INTO Meta_Data(_name, _date, _loca, ready) VALUES(?, ?, ?, ?)'
        cur.execute(query, (name, date, loca, ready_flag))
        conn.commit()
        waitQ2.put(1)                                       #새로 생성된 clip들을 db에 insert하고 대기큐2 활성화

def inter_thread() :
    temp = ""                                                   #To store latest name
    sql = 'SELECT _name FROM Meta_Data WHERE ready=0'
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows :                                           #all of not uploaded clip put upload queue
        clip_name = row[0]
        uploadQ.put(clip_name)
        temp = clip_name
    waitQ1.put(1)                                        # 이전에 생성되고 처리가 안된 ready=0인 애들을 먼저 uploadQ에 다 넣어주고 대기Queue를 풀어줌
    while True :
        wait = waitQ2.get()                             #새로 생성된 clip들이 db에 insert 될때까지 대기
        sql = 'SELECT _name FROM Meta_Data ORDER BY _id DESC LIMIT 1;'
        cur.execute(sql)
        fetch_name = cur.fetchone()                             #실행 결과(테이블 마지막에 저장된 clip 명)가 튜플형태로 저장됨
        name = fetch_name[0]
        if temp == name :                                    #아직 테이블에 데이터가 추가되지 않았을 때
            continue
        else :                                                  #테이블에 최신값이 추가되었을때
            uploadQ.put(name)                                   #t새로 생성된 clip을 update 위해서 uploadQ에 삽입
            temp = name
            continue

def update_db(clip_name, ipfsAdd, enc_key) :
    print('DB update start')
    sql = 'UPDATE Meta_Data SET ipfs_hash=?, Enc_AES=?, ready=?, MDR_id=? WHERE _name=?'
    ready_flag = 1
    merkle_root = 1
    clip_hash=ipfsAdd.decode().split(' ')[-2]
    upDB = (clip_hash, str(enc_key), ready_flag, merkle_root, clip_name)
    cur.execute(sql, upDB)
    conn.commit()
    sql = 'SELECT * FROM Meta_Data WHERE _name=?'
    selDB = (clip_name,)
    cur.execute(sql, selDB)
    inqueue = cur.fetchone()
    deployQ.put(str(inqueue))

class LogHandler(PatternMatchingEventHandler) :        #Class of monitoring module(watchdog)
    def __init__(self) :                                #Call constructor
        super(LogHandler, self).__init__(ignore_patterns=["*/ex.log"])
        f = open(fileLog, 'w')            #reset fileLog.txt whenever program start
        f.seek(0)
        f.truncate()
        f.close()
    def on_created(self, event) :           # when create event occured, start
        super(LogHandler, self).on_created(event)
        what = 'directory'
        self.eventLog = "created, " + event.src_path
        print(self.eventLog)
        with open(fileLog, 'a') as fout:                #write to filelog.txt about created video clip(not significant)
            fout.write(self.eventLog.split('/')[-1])
            fout.write('\n')
            fout.close()
        insertQ.put(self.eventLog.split('/')[-1])     #important. put name of file(clip) to queue

""""""
def upload_thread(temp_year, temp_month, temp_day) :
    time.sleep(10)                           #An upload thread that handles the main task, encrypts the clip, receives the hash value returned since IPFS add, and passes it to the insert_db function

    while True:                                 #loop
        now = datetime.now()                    #이후 카메라별 IPFS 디렉토리를 갱신할 때에 월/별 구분하기 위해 현재날짜 객체를 생성
        check = uploadQ.queue[0]                  #queue에 삽입된 영상 파일의 이름을 저장하는 변수(암호화가 아직 안됨)
        temp = os.path.getsize(Camerapath + check)  #파일의 size를 이용해서 영상이 다 받아졌는지 확인하기 위한 size 체크
        time.sleep(5)                               #파일의 size가 5초가 지나도 그대로이면 파일이 다 받아진것으로 판단하고 업로드 작업 수행
        checkSize = Camerapath + check
        if os.path.getsize(checkSize) == temp :
            toAdd = uploadQ.get()     #queue에 삽입된 영상 파일을 get으로 가져온다 그리고 그 파일의 이름은 toAdd에 저장.
            print(toAdd)
            AES_key = EncDec.Random.new().read(32)     #영상 파일 암호화를 위해 AES_key를 생성함
            enc_key = EncDec.rsa_enc(AES_key)          #AES_key를 public_key를 이용해서 암호화
            dec_key = EncDec.rsa_dec(enc_key)          #이건 솔직히 필요 없음. 이후 복호화 하기 위함 (private_key로 복호화)
            in_filename = Camerapath + toAdd.strip()   #암호화 할 영상 파일의 위치 및 파일명(즉 Camera_/영상파일)
            os.chdir(encDir)                           #암호화된 영상 파일이 저장될 위치, 즉 encCamera_에 저장
            EncDec.encrypt_file(AES_key, in_filename, out_filename=toAdd.strip())   #AES_key를 이용해서 영상 파일을 암호화
            print('enc!!!!')
            time.sleep(2)                               #2초간 정지 후 암호화된 영상 파일을 ipfs add
            try :
                ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            except :
                daemonQueue.put(1)
                time.sleep(30)
                ipfsAdd=subprocess.check_output('/usr/local/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            clip_name=ipfsAdd.decode().split(' ')[-1].strip()
            time.sleep(30)

            ctime = os.path.getctime(Camerapath + clip_name)    #영상 클립 생성 시간으로 머클디렉토리 작업할거
            temp = str(datetime.fromtimestamp(ctime))
            temp1 = temp.split(' ')[0].replace("-", "/")
            day_dir = temp1.split('/')[2]
            month_dir = temp1.split('/')[1]
            year_dir = temp1.split('/')[0]

            day_path = 'rootDir'+'/'+year_dir+'/'+month_dir+'/'+day_dir
            month_path = 'rootDir'+'/'+year_dir+'/'+month_dir
            year_path = 'rootDir'+'/'+year_dir
            sql = 'SELECT EXISTS (SELECT * FROM merkleDir WHERE path=?)'
            day = (day_path,)
            month = (month_path,)
            year = (year_path,)
            cur.execute(sql,day)
            check_day = cur.fetchone()[0]
            cur.execute(sql,month)
            check_month = cur.fetchone()[0]
            cur.execute(sql,year)
            check_year = cur.fetchone()[0]

            if check_year == 1 :      #암호화된 영상 파일을 IPFS 디렉토리에 저장 후 갱신하기 위한 조건문 시작, 년도/월/일 구분
                if check_month == 1 :    #년도와 월이 변화가 없다면
                    if check_day == 1 :    #년도와 월과 일이 변화가 없다면 dirUpdate1 함수 실행
                        root_hash = updateDir.dirUpdate1(year_dir, month_dir, day_dir, ipfsAdd)
                    elif check_day == 0 :  #년도와 월은 변화가 없지만 일이 변했다면
                        root_hash = updateDir.dirUpdate1_1(year_dir, month_dir, day_dir, ipfsAdd)
                elif check_month == 0 :  #년도는 같지만 월이 다르다면
                    root_hash = updateDir.dirUpdate2(year_dir, month_dir, day_dir, ipfsAdd)  #년도는 같지만 월이 다른경우 dirUpdate2 실행시켜줌, 월이 다르다면 당연히 일도 다름
            elif check_year == 0 : #년도가 바뀌었을 때에는 1월 1일이니까 month=1, day=1로 변화
                root_hash = updateDir.dirUpdate3(year_dir, month_dir, day_dir, ipfsAdd)
            update_db(clip_name, ipfsAdd, enc_key)                 #ipfs의 hash와 암호화된 AES_key를 인자로 넘겨서 DB thread 함수 호출
            uploadQ.task_done()                           #queue작업이 수행되었음을 알림.
            print('DB update task done')
            os.remove(Camerapath + toAdd)              #업로드 수행 이후 영상 파일 제거
            os.remove(encDir + toAdd)                  #업로드 수행 이후 암호화된 영상 파일 제거


""""""
def deploy() :              #스마트컨트랙트에 메타데이터를 저장하기 위한 스레드
    while True :
        i = 0
        setData = deployQ.get()      #queue2에 저장된 데이터(데이터베이스에서 추출한 마지막 열의 메타데이터)를 setData에 저장
        tx_receipt = w3.eth.getTransactionReceipt('0xd501b20ee29b361f7babde65bbc78a13b583e8936a09aa235cde71289c39ebdb') #스마트 컨트랙트의 주소를 추출하기 위해 트랜잭션의 주소를 가져옴
        contract_address = tx_receipt['contractAddress']
        contract_instance = contract(contract_address)#컨트랙트 주소를 이용해서 컨트랙트 인스턴스 생성
        # Set
        tx = contract_instance.transact({"from": w3.eth.accounts[0],"gas": 500000}).insertData(str(setData))#스마트컨트랙트에 setData를 저장함. 저장하는 주체는 account[0]이고 가스는 500000으로 설정
        print('smart contract value inserted value : {} '.format(setData))
        time.sleep(2)
        #while w3.eth.getTransactionReceipt(tx) is None :            #트랜잭션이 채굴될 때 까지 대기
        #    time.sleep(3)
        while True :
            try :
                tx_hash = w3.eth.getTransactionReceipt(tx)
                print('transaction submitting')
                break
            except :
                continue
        while w3.eth.getTransactionReceipt(tx) is None :
            time.sleep(3)

        temp = contract_instance.call().getIndex()                  #컨트랙트내의 배열 인덱스를 가져옴, 이 인덱스를 가지고 컨트랙트 배열에 저장된 메타데이터를 추출
        print('last index : {} '.format(temp))
        print('inserted value get : {} '.format(contract_instance.call().getData(temp)))
        deployQ.task_done()
        print('deploy task done')


if __name__ == '__main__' :
    insert_thread = threading.Thread(target=insert_db)
    interface_thread = threading.Thread(target=inter_thread)
    #Camera_thread = threading.Thread(target=Camera, args=(0,))
    #Camera_thread.daemon = True
    #Camera2_thread = threading.Thread(target=Camera2, args=(0,))
    #Camera2_thread.daemon = True
    #Camera3_thread = threading.Thread(target=Camera3, args=(0,))
    #Camera3_thread.daemon = True
    deplpy_thread = threading.Thread(target = deploy)
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=Camerapath, recursive=True)
    observer.start()
    insert_thread.start()
    interface_thread.start()
    #Camera_thread.start()
    #Camera2_thread.start()
    #Camera3_thread.start()
    time.sleep(3)
    upload = threading.Thread(target = upload_thread, args=(now.year, now.month, now.day))
    upload.start()
    deplpy_thread.start()
    daemon_thread = threading.Thread(target=daemon)
    daemon_thread.start()


    try :
        while True :
		          time.sleep(1)
    except KeyboardInterrupt :
        observer.stop()
    observer.join()
