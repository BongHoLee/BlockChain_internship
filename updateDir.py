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
emptyDir = 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn'



def dirUpdate1(temp_year, temp_month, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()
    clip_hash=ipfsAd.decode().split(' ')[-2]
    if 'aCAM' in clip_name :
        sql='SELECT hash FROM Camera1 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        sql='SELECT hash FROM Camera2 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        sql='SELECT hash FROM Camera3 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
def dirUpdate2(temp_year, temp_month, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()
    clip_hash=ipfsAd.decode().split(' ')[-2]
    if 'aCAM' in clip_name :
        sql='INSERT INTO Camera1 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera1 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        sql='INSERT INTO Camera2 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera2 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        sql='INSERT INTO Camera3 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera3 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
#년도 다름
def dirUpdate3(temp_year, temp_month, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()
    clip_hash=ipfsAd.decode().split(' ')[-2]
    if 'aCAM' in clip_name :
        sql='INSERT INTO Camera1 (path, hash) VALUES (?, ?)'
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera1 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera1 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera2 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera2 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
        insert_value = ('rootDir/'+str(temp_year), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))
        cur.execute(sql, insert_value)
        conn.commit()
        sql='SELECT hash FROM Camera3 WHERE path=?'
        month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),)
        cur.execute(sql, month_path)
        month_hash = str(cur.fetchone()[0])
        year_path=('rootDir/'+str(temp_year),)
        cur.execute(sql, year_path)
        year_hash = str(cur.fetchone()[0])
        root_path = ('rootDir',)
        cur.execute(sql, root_path)
        root_hash = str(cur.fetchone()[0])
        up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
        sql = 'UPDATE Camera3 SET hash=? WHERE path=?'
        update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))
        cur.execute(sql, update)
        conn.commit()
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
