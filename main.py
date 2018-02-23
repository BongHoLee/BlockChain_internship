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
insertQ = Queue()                                                   #Queue for recieve video clip file name
deployQ = Queue()                                                   #Upload metadata of clip to DB and store it in queue2 to transmit the metadata to smartcontact
daemonQueue = Queue()                                               #exception handling queue for ipfs daemon
now = datetime.now()                                                #store now datetime
uploadQ = Queue()                                                   #to call upload thread from inter_thread
waitQ1 = Queue()                                                    #wait Queue1 for shared resource access restriction
waitQ2 = Queue()                                                    #wait Queue2 for shared resource(Database table) access restriction



rpc_url = "http://192.168.1.2:8545"                         #HTTPProvider to communication wtih Mac mini(server)'s geth
w3 = Web3(HTTPProvider(rpc_url, request_kwargs={'timeout': 500}))
contract = w3.eth.contract(abi=[{'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getData', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])


def daemon() :                      #exception handling when ipfs daemon terminates abnormally
    try:
        daemonQueue.get()           #wait for error flag(daemon quit) in the daemonQueue
        restart = subprocess.check_output('/Users/leebongho/work/bin/ipfsrepo fsck', stderr=subprocess.STDOUT, shell=True)
        print('daemon resart')
        redaemon = subprocess.check_output('/Users/leebongho/work/bin/ipfsdaemon', stderr = subprocess.STDOUT, shell=True)
    except :
        daemon()

"""openRTSP 카메라 구동 스레드"""
def Camera2(i) :                                        #IP camera play thread (start openRTSP)
    os.chdir(Camerapath)
    i+=1
    temp = datetime.now()
    nowDatetime = temp.strftime('%Y:%m:%d:%H:%M:%S')
    try :
        sub = subprocess.check_output('openRTSP -D 3 -B 250000 -b 250000 -c -i -F bCAM-'+str(nowDatetime)+' -P 60 rtsp://192.168.1.217//stream1', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera2(i)

def Camera3(i) :                                        #IP camrea play thread (start openRTSP)
    os.chdir(Camerapath)
    i+=1
    temp = datetime.now()
    nowDatetime = temp.strftime('%Y:%m:%d:%H:%M:%S')
    try :
        sub = subprocess.check_output('openRTSP -D 3 -B 250000 -b 250000 -c -i -F cCAM-'+str(nowDatetime)+' -P 60 rtsp://192.168.1.18:8554/unicast', stderr=subprocess.STDOUT, shell=True)
    except :
        print("error")
        Camera3(i)

def Camera(i) :                                         #IP camera play thread (start openRTSP)
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
    wait = waitQ1.get()                             #wait until  inter_thread put all Datas that have status=0  to uploadQ(Database Concurrent reference restrict)
    while True :
        name = insertQ.get()                                #start insert to DB table newly created clip
        print('basic insert start')
        ctime = os.path.getctime(Camerapath + name)     #To insert create date of clip
        dt = datetime.fromtimestamp(ctime)                  #To insert create date of clip
        g = geocoder.ip('me')                               #To insert location of clip
        date = str(dt)                                      #transform to string type
        loca = str(g.latlng)                                #transform to string type
        status_flag = 0                                     #set to status (stats=0 means clip was just creation, status=1 means clip was encrypted and deployed to smart contract(blockchain))
        query = 'INSERT INTO Meta_Data(_name, _date, _loca, status) VALUES(?, ?, ?, ?)'         #newly created clip insert some column to Meta_Data table except ipfs_hash, Enc_AES, MRD_id(Foreign key)
        cur.execute(query, (name, date, loca, status_flag))
        conn.commit()
        waitQ2.put(1)                                       #wait2 Queue unlock to newly created data put to upload_Thread(via inter_thread)

def inter_thread() :                                            #inter_thread (interface of Meta_Data Table and upload_thread)
    temp = ""                                                   #To store latest _name of metadata with status == 0
    sql = 'SELECT _name FROM Meta_Data WHERE status=0'          #SELECT all of _name of metadata with status == 0
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows :                                           #store to row one by one (_name of metadata with status == 0)
        clip_name = row[0]                                      #store clip_name
        uploadQ.put(clip_name)                                  #put clip_name to uploadQ for upload work(ipfs add, update merkle directory, deploy to smart contract)
        temp = clip_name                                        #latest clip_name that putted in uploadQ
    waitQ1.put(1)                                        # waitQ1 Queue unlock to make insert_db thread to work
    while True :
        wait = waitQ2.get()                             #wati for insert_db thread work done
        sql = 'SELECT _name FROM Meta_Data ORDER BY _id DESC LIMIT 1;'      #select newly inserted metadata
        cur.execute(sql)
        fetch_name = cur.fetchone()                             #select query result
        name = fetch_name[0]                                    #convert to string type(name = newly inserted metadata)
        if temp == name :                                    #if newly metadata not inserted, call continue
            continue
        else :                                                  #if newly metadata inserted, put to uploadQ
            uploadQ.put(name)                                   #put to uploadQ
            temp = name                                         #temp keep up to date _name of metadata
            continue

def update_db(clip_name, ipfsAdd, enc_key) :                    #update_db method : get status==0 metadata name, ipfs_hash, Enc_AES, update Database, and update status == 1
    print('DB update start')
    sql = 'UPDATE Meta_Data SET ipfs_hash=?, Enc_AES=?, status=?, MDR_id=? WHERE _name=?'       #update query about metadata's ipfs_hash, Enc_Aes, status, MDR_id column
    status_flag = 1
    merkle_root = 1
    clip_hash=ipfsAdd.decode().split(' ')[-2]                                                   #make ipfs_hash of clip
    upDB = (clip_hash, str(enc_key), status_flag, merkle_root, clip_name)
    cur.execute(sql, upDB)
    conn.commit()                                                                               #DB update is done
    sql = 'SELECT * FROM Meta_Data WHERE _name=?'                                               #select updated metadata tuple
    selDB = (clip_name,)
    cur.execute(sql, selDB)
    inqueue = cur.fetchone()
    deployQ.put(str(inqueue))                                                                   #put to deploy thread for deploy to smart contract

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
        check = uploadQ.queue[0]                  #get the value stored in uploadQ (not queue.get(), not pop from queue)
        temp = os.path.getsize(Camerapath + check)  #store current size of clip to check if streaming is complete
        time.sleep(5)                               #wait for 5 seconds
        checkSize = Camerapath + check              #store size of clip after 5 seconds
        if os.path.getsize(checkSize) == temp :     #compare sizes changes between 5 seconds (if not eqaul, streaming is not complete)
            toAdd = uploadQ.get()     #get complete(streaming) clip from uploadQ.
            print(toAdd)
            AES_key = EncDec.Random.new().read(32)     #create AES_KEY to encryption(clip encryption)
            enc_key = EncDec.rsa_enc(AES_key)          #encrypt AES_KEY using public_key (enc_key == encrypted AES_KEY : Enc_AES)
            dec_key = EncDec.rsa_dec(enc_key)          #to decrypt afterwards, (dec_key == AES_KEY)
            in_filename = Camerapath + toAdd.strip()   #store the name of the clip to be encrypted(즉 Camera_/영상파일)
            os.chdir(encDir)                           #work directory is encCamera_(ecrypted clip will be created in this directory)
            EncDec.encrypt_file(AES_key, in_filename, out_filename=toAdd.strip())   #encrypt the clip using AES_KEY
            print('enc!!!!')
            print('srtat IPFS Add')
            time.sleep(2)                               #wait for 2 seconds
            try :                                       #ipfs add about encrypted clip
                ipfsAdd=subprocess.check_output('/Users/leebongho/work/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            except :
                daemonQueue.put(1)                      #if ipfs daemon was terminated, restart
                time.sleep(30)
                ipfsAdd=subprocess.check_output('/Users/leebongho/work/bin/ipfs add ' + encDir + toAdd.strip(), stderr=subprocess.STDOUT, shell=True)
            clip_name=ipfsAdd.decode().split(' ')[-1].strip()                   #store encrypted clip_name(eqaul to original name of clip)
            time.sleep(30)
            print('IPFS Add Done. updating Merkle Directory')                   #ipfs add done, start merkle directroy update

            ctime = os.path.getctime(Camerapath + clip_name)    #to store creation time of the clip
            temp = str(datetime.fromtimestamp(ctime))           #convert to string
            temp1 = temp.split(' ')[0].replace("-", "/")        #convert to year/month/day
            day_dir = temp1.split('/')[2]                       #day_dir store day
            month_dir = temp1.split('/')[1]                     #month_dir store month
            year_dir = temp1.split('/')[0]                      #year_dir store year

            day_path = 'rootDir'+'/'+year_dir+'/'+month_dir+'/'+day_dir     #day_path is rootDir/year/month/day
            month_path = 'rootDir'+'/'+year_dir+'/'+month_dir               #month_path is rootDir/year/month
            year_path = 'rootDir'+'/'+year_dir                              #year_path is rootDir/year
            sql = 'SELECT EXISTS (SELECT * FROM merkleDir WHERE path=?)'    #make sure it already exists. if exists, return 1 nor return 0
            day = (day_path,)
            month = (month_path,)
            year = (year_path,)
            cur.execute(sql,day)
            check_day = cur.fetchone()[0]                                   #Verify that the day directory exists that matches the date in the file(true: 1, false : 0)
            cur.execute(sql,month)
            check_month = cur.fetchone()[0]                                 #Verify that the month directory exists that matches the date in the file(true: 1, false : 0)
            cur.execute(sql,year)
            check_year = cur.fetchone()[0]                                  #Verify that the year directory exists that matches the date in the file(true: 1, false : 0)

            if check_year == 1 :      #if year directory already exists in merkleDir table, check month directory
                if check_month == 1 :    #if month directory already exists in merkleDir tble, check day directory
                    if check_day == 1 :    #if year/month/day directory already exists in merkleDir table, call updateDir.dirUpdate1 function
                        root_hash = updateDir.dirUpdate1(year_dir, month_dir, day_dir, ipfsAdd)
                    elif check_day == 0 :  #if year/month directory already exsits but year/month/day directory is not exsits in merkleDir table, call updateDir.dirUpdate1_1 function
                        root_hash = updateDir.dirUpdate1_1(year_dir, month_dir, day_dir, ipfsAdd)
                elif check_month == 0 :  #if year directory already exsits but year/month directory and year/month/day directory are not eixsts in merkleDir table, call updateDir.dirUpdate2 function
                    root_hash = updateDir.dirUpdate2(year_dir, month_dir, day_dir, ipfsAdd)  #
            elif check_year == 0 : #if year directory, year/month directory and year/month/day directory are not exsits in merkleDir table, call updateDir.dirUpdate3 function
                root_hash = updateDir.dirUpdate3(year_dir, month_dir, day_dir, ipfsAdd)
            print('Update merkle Direcotry Done. start deploying to Smart contract')            #merkleDir update is done
            update_db(clip_name, ipfsAdd, enc_key)                 #pass the arguments to update_db method to update Meta_Data table(about ipfs_hash, Enc_AES, status, MDR_id)
            uploadQ.task_done()                           #uploadQ was done
            print('DB update task done')
            os.remove(Camerapath + toAdd)              #if update Database, remove updated clip from Camera_ directroy
            os.remove(encDir + toAdd)                  #if update Database, remove updated clip from encCamera_ directory


""""""
def deploy() :              #deploy thread to deploy metadata from Meta_Data table to smart contract
    while True :
        i = 0
        setData = deployQ.get()      #get metadata from deployQ(inserted by update_db)
        print('deploy thread start!')
        tx_receipt = w3.eth.getTransactionReceipt('0xd501b20ee29b361f7babde65bbc78a13b583e8936a09aa235cde71289c39ebdb') #trasaction address for smart contract address
        contract_address = tx_receipt['contractAddress']                #call smart contract address
        contract_instance = contract(contract_address)#create contract_instance using smartcontact address
        # Set
        tx = contract_instance.transact({"from": w3.eth.accounts[0],"gas": 500000}).insertData(str(setData))#deploy metadata(setData) to smartcontract using accounts (eth.accounts[0]) and gas limit 500000
        time.sleep(2)
        #while w3.eth.getTransactionReceipt(tx) is None :            #wait for mining
        #    time.sleep(3)
        while True :                                                #wait for mining
            try :
                tx_hash = w3.eth.getTransactionReceipt(tx)
                print('transaction submitting')
                break
            except :
                continue
        while w3.eth.getTransactionReceipt(tx) is None :            #if mining done, break from while
            time.sleep(3)

        temp = contract_instance.call().getIndex()                  #get smart index of smart contract's metadata array
        print('last index : {} '.format(temp))
        print('inserted value get from smart contract : {} '.format(contract_instance.call().getData(temp)))    #print metadata from smart contract for check
        deployQ.task_done()
        print('deploy task done')


if __name__ == '__main__' :
    insert_thread = threading.Thread(target=insert_db)          #define insert_db thread
    interface_thread = threading.Thread(target=inter_thread)    #define inter_thread thread
    #Camera_thread = threading.Thread(target=Camera, args=(0,)) #define Camera thread
    #Camera_thread.daemon = True
    #Camera2_thread = threading.Thread(target=Camera2, args=(0,))   #define Camera2 thread
    #Camera2_thread.daemon = True
    #Camera3_thread = threading.Thread(target=Camera3, args=(0,))   #define Camera3 thread
    #Camera3_thread.daemon = True
    deplpy_thread = threading.Thread(target = deploy)               #define deploy thread
    event_handler = LogHandler()                                    #define monitoring thread
    observer = Observer()                                           #define monitoring thread
    observer.schedule(event_handler, path=Camerapath, recursive=True)   #define monitoring thread
    observer.start()                                                #monitoring thread start
    insert_thread.start()                                           #insert_db thread start
    interface_thread.start()                                        #inter_thread thread start
    #Camera_thread.start()                                          #Camera thread start
    #Camera2_thread.start()                                         #Camera2 thread start
    #Camera3_thread.start()                                         #Camera3 thread start
    time.sleep(3)
    upload = threading.Thread(target = upload_thread, args=(now.year, now.month, now.day))  #define upload_thread thread
    upload.start()                                                  #upload_thread start
    deplpy_thread.start()                                           #deploy thread start
    daemon_thread = threading.Thread(target=daemon)                 #define daemon thread
    daemon_thread.start()                                           #daemon_thread start


    try :
        while True :
		          time.sleep(1)
    except KeyboardInterrupt :
        observer.stop()
    observer.join()
