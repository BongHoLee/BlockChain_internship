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
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
emptyDir = 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn' #IPFS directory에 새로운 디렉토리를 생성하기 위한 해시


def dirUpdate1(temp_year, temp_month, temp_day, ipfsAd) :         #년도/월/일이 이전과 같을 때
    clip_name=ipfsAd.decode().split(' ')[-1].strip()    #영상 명을 추출
    clip_hash=ipfsAd.decode().split(' ')[-2]            #영상의 IPFS해시를 추출
    if 'aCAM' in clip_name :                            #영상 이름이 aCAM이라면 조건문 실행
        sql='SELECT hash FROM Camera1 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'bCAM' in clip_name :
        sql='SELECT hash FROM Camera2 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'cCAM' in clip_name :
        sql='SELECT hash FROM Camera3 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
def dirUpdate1_1(temp_year, temp_month, temp_day, ipfsAd) :         #년도/월/이 같지만 일이 다를때
    clip_name=ipfsAd.decode().split(' ')[-1].strip()    #영상 명을 추출
    clip_hash=ipfsAd.decode().split(' ')[-2]            #영상의 IPFS해시를 추출
    if 'aCAM' in clip_name :                            #영상 이름이 aCAM이라면 조건문 실행
        sql='INSERT INTO Camera1 (path, hash) VALUES (?, ?)'        #새로운 day 디렉토리를 추가
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera1 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'bCAM' in clip_name :
        sql='INSERT INTO Camera2 (path, hash) VALUES (?, ?)'        #새로운 day 디렉토리를 추가
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera2 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'cCAM' in clip_name :
        sql='INSERT INTO Camera3 (path, hash) VALUES (?, ?)'        #새로운 day 디렉토리를 추가
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera3 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r

#년 같고 월 다름
def dirUpdate2(temp_year, temp_month, temp_day, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()
    clip_hash=ipfsAd.decode().split(' ')[-2]
    if 'aCAM' in clip_name :
        sql='INSERT INTO Camera1 (path, hash) VALUES (?, ?)'    #새로운 월을 IPFS diecrtory에 추가하기 전에 데이터베이스에 먼저 insert
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))   #위의 emptyDir이 IPFS의 빈 디렉토리 해시임, 즉 이 해시를 link해주면 기존의 IPFS directory에 빈 디렉토리가 생성됨
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir)) #새로운 day도 insert
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera1 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'bCAM' in clip_name :
        sql='INSERT INTO Camera2 (path, hash) VALUES (?, ?)'    #새로운 월을 IPFS diecrtory에 추가하기 전에 데이터베이스에 먼저 insert
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))   #위의 emptyDir이 IPFS의 빈 디렉토리 해시임, 즉 이 해시를 link해주면 기존의 IPFS directory에 빈 디렉토리가 생성됨
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir)) #새로운 day도 insert
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera2 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'cCAM' in clip_name :
        sql='INSERT INTO Camera3 (path, hash) VALUES (?, ?)'    #새로운 월을 IPFS diecrtory에 추가하기 전에 데이터베이스에 먼저 insert
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))   #위의 emptyDir이 IPFS의 빈 디렉토리 해시임, 즉 이 해시를 link해주면 기존의 IPFS directory에 빈 디렉토리가 생성됨
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir)) #새로운 day도 insert
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera3 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
#년도 다름 즉 월, 일 둘다 갱신됨
def dirUpdate3(temp_year, temp_month, temp_day, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()
    clip_hash=ipfsAd.decode().split(' ')[-2]
    if 'aCAM' in clip_name :
        sql='INSERT INTO Camera1 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))   #년도가 다르다면 년도, 월(1), 일(1) 세 개의 디렉토리를 생성해야 하므로 먼저 데이터베이스에 INSERT 해줌
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        sql='SELECT hash FROM Camera1 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'bCAM' in clip_name:
        sql='INSERT INTO Camera2 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))   #년도가 다르다면 년도, 월(1), 일(1) 세 개의 디렉토리를 생성해야 하므로 먼저 데이터베이스에 INSERT 해줌
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        sql='SELECT hash FROM Camera2 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
    elif 'cCAM' in clip_name:
        sql='INSERT INTO Camera3 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))   #년도가 다르다면 년도, 월(1), 일(1) 세 개의 디렉토리를 생성해야 하므로 먼저 데이터베이스에 INSERT 해줌
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))
        sql='SELECT hash FROM Camera3 WHERE path=?'     #Camera1 테이블에서 path에 해당하는 ipfs hash를 가져옴
        day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #현재 날짜에 해당하는 ipfs directory에서 day의 이름을 저장
        cur.execute(sql, day_path)          #sql실행
        day_hash = str(cur.fetchone()[0])   #sql실행 결과로 반환된 ipfs day hash를 day_hash에 저장
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #현재 날짜에 해당하는 ipfs directory에서 month 디렉토리의 이름을 저장
        cur.execute(sql, month_path) #sql 실행
        month_hash = str(cur.fetchone()[0]) #sql 실행 결과로 반환된 ipfs month hash를 month_hash에 저장
        year_path=('rootDir/'+str(temp_year),)  #위와 같은 작업을 year를 기준으로 실행
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)                #위와 같은 작업을 rootDirectory를 기준으로 실행
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #기존의 IPFS directory에 day에 해당하는 위치에 영상을 link했을 때 반환되는 수정된 day의 hash를 저장
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'      #수정된 month의 hash로 데이터베이스를 업데이트
        update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #갱신된 day로 table update
        cur.execute(sql, update)
        conn.commit()
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #갱신된 month의 hash를 저장
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #갱신된 month로 table update
        cur.execute(sql, update)
        conn.commit()   #업데이트 사항 저장
        up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_y), 'rootDir/'+str(temp_year))
        cur.execute(sql, update)
        conn.commit()
        up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        update=(str(up_r), 'rootDir')
        cur.execute(sql, update)
        conn.commit()
        print(up_r)
        return up_r
