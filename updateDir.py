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
emptyDir = 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn' #A hash to create a new directory in the IPFS directory.


def dirUpdate1(temp_year, temp_month, temp_day, ipfsAd) :         #When year / month / day already exists
    clip_name=ipfsAd.decode().split(' ')[-1].strip()    #Extract clip name
    clip_hash=ipfsAd.decode().split(' ')[-2]            #Extract clip hash
    sql='SELECT hash FROM merkleDir WHERE path=?'     #Get the ipfs hash corresponding to path in the merkleDir table.
    day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #store year/month/day path to select matched hash from merkleDir
    cur.execute(sql, day_path)          #run sql
    day_hash = str(cur.fetchone()[0])   #Save the year/month/day hash returned by sql as day_hash.
    month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #store year/month path to select matched hash from merkleDir
    cur.execute(sql, month_path) #run sql
    month_hash = str(cur.fetchone()[0]) #Save the year/month hash returned by sql as month_hash
    year_path=('rootDir/'+str(temp_year),)  #store year path to select matched hash from merkleDir
    cur.execute(sql, year_path)#run sql
    year_hash = str(cur.fetchone()[0])  #Save the year hash returned by sql as year_hash
    root_path = ('rootDir',)                #same about rootDir
    cur.execute(sql, root_path)
    root_hash = str(cur.fetchone()[0])
    up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #Returns a hash of the modified year / month / day directory returned when the clip is linked to the year / month / day directory.
    sql = 'UPDATE merkleDir SET hash=? WHERE path=?'      #Query to update the modified hash(day).
    update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #table update about modified path (year/month/day)
    cur.execute(sql, update)
    conn.commit()
    up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #Returns a hash of the modified year / month directory returned when the day directory is linked to the year/month directory
    update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #Query to update modifed hash(month/day)
    cur.execute(sql, update)
    conn.commit()   #업데이트 사항 저장
    up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()  #Returns a hash of the modified year directory returned when the month/day directory is linked to the year directory
    update=(str(up_y), 'rootDir/'+str(temp_year))               #Query to update modified hash(year/month/day)
    cur.execute(sql, update)
    conn.commit()
    up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()   #Returns a hash of the modified rootDir directory returned when the year/month/day directory is linked to the rootDir directory
    update=(str(up_r), 'rootDir')                               #Query to update modified hash(rootDir/year/month/day)
    cur.execute(sql, update)
    conn.commit()
    print(up_r)
    return up_r
def dirUpdate1_1(temp_year, temp_month, temp_day, ipfsAd) :         #year / month exists but year / month / day does not exist.
    clip_name=ipfsAd.decode().split(' ')[-1].strip()    #Extract clip name
    clip_hash=ipfsAd.decode().split(' ')[-2]            #Extract clip hash
    sql='INSERT INTO merkleDir (path, hash) VALUES (?, ?)'        #insert new year/month/day
    insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir))         #day directory is empty directory(newly created)
    cur.execute(sql, insert_value)                      #insert query execute
    conn.commit()
    sql='SELECT hash FROM merkleDir WHERE path=?'     #Get the ipfs hash corresponding to path in the merkleDir table.
    day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #store year/month/day path to select matched hash from merkleDir
    cur.execute(sql, day_path)          #sql실행
    day_hash = str(cur.fetchone()[0])   #Save the year/month/day hash returned by sql as day_hash.
    month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #store year/month path to select matched hash from merkleDir
    cur.execute(sql, month_path) #sql run
    month_hash = str(cur.fetchone()[0]) #Save the year/month hash returned by sql as month_hash
    year_path=('rootDir/'+str(temp_year),)  #store year path to select matched hash from merkleDir
    cur.execute(sql, year_path)
    year_hash = str(cur.fetchone()[0])      #Save the year hash returned by sql as year_hash
    root_path = ('rootDir',)                #same
    cur.execute(sql, root_path)
    root_hash = str(cur.fetchone()[0])
    up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #Same as above dirUpdate1 function
    sql = 'UPDATE merkleDir SET hash=? WHERE path=?'      ##Same as above dirUpdate1 function
    update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #Same as above dirUpdate1 function
    cur.execute(sql, update)
    conn.commit()
    up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #Same as above dirUpdate1 function
    update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #Same as above dirUpdate1 function
    cur.execute(sql, update)
    conn.commit()   #업데이트 사항 저장
    up_y = subprocess.check_output('/usr/local/bin/ipfs object patch '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()  #Same as above dirUpdate1 function
    update=(str(up_y), 'rootDir/'+str(temp_year))
    cur.execute(sql, update)
    conn.commit()
    up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()   #Same as above dirUpdate1 function
    update=(str(up_r), 'rootDir')
    cur.execute(sql, update)
    conn.commit()
    print(up_r)
    return up_r

#exists year directory but year/month and year/month/day not exists
def dirUpdate2(temp_year, temp_month, temp_day, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()          #Extract clip name
    clip_hash=ipfsAd.decode().split(' ')[-2]                  #Extract clip hash
    sql='INSERT INTO merkleDir (path, hash) VALUES (?, ?)'    #insert query to year/month and year/month/day
    insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))   # year/month directory is empty directory(newly created)
    cur.execute(sql, insert_value)
    conn.commit()
    insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir)) #year/month/day directory is empty directory(newly creatd)
    cur.execute(sql, insert_value)
    conn.commit()                                     ###################The following is equivalent to the updateDir1 function above####################
    sql='SELECT hash FROM merkleDir WHERE path=?'     #
    day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #
    cur.execute(sql, day_path)          #
    day_hash = str(cur.fetchone()[0])   #
    month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #
    cur.execute(sql, month_path) #
    month_hash = str(cur.fetchone()[0]) #
    year_path=('rootDir/'+str(temp_year),)  #
    cur.execute(sql, year_path)
    year_hash = str(cur.fetchone()[0])
    root_path = ('rootDir',)                #
    cur.execute(sql, root_path)
    root_hash = str(cur.fetchone()[0])
    up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #
    sql = 'UPDATE merkleDir SET hash=? WHERE path=?'      #
    update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #
    cur.execute(sql, update)
    conn.commit()
    up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #
    update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #
    cur.execute(sql, update)
    conn.commit()   #
    up_y = subprocess.check_output('/usr/local/bin/ipfs object patc#h '+ year_hash +' add-link ' + str(temp_month) + ' ' + up_m, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
    update=(str(up_y), 'rootDir/'+str(temp_year))
    cur.execute(sql, update)
    conn.commit()
    up_r = subprocess.check_output('/usr/local/bin/ipfs object patch '+ root_hash +' add-link ' + str(temp_year) + ' ' + up_y, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip()
    update=(str(up_r), 'rootDir')
    cur.execute(sql, update)
    conn.commit()
    print(up_r)
    return up_r
#not exists year
def dirUpdate3(temp_year, temp_month, temp_day, ipfsAd) :
    clip_name=ipfsAd.decode().split(' ')[-1].strip()        #Extract clip name
    clip_hash=ipfsAd.decode().split(' ')[-2]                #Extract clip hash
    sql='INSERT INTO merkleDir (path, hash) VALUES (?, ?)'      #insert query to year, year/month and year/month/day
    insert_value = ('rootDir/'+str(temp_year), str(emptyDir))   ##year directory is empty directory(newly created)
    conn.commit()
    insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month), str(emptyDir))   #  year/month directory is empty directory(newly created)
    cur.execute(sql, insert_value)
    conn.commit()
    insert_value = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day), str(emptyDir)) # # year/month/day directory is empty directory(newly created)
    cur.execute(sql, insert_value)
    conn.commit()

    sql='SELECT hash FROM merkleDir WHERE path=?'     ###################The following is equivalent to the updateDir1 function above####################
    day_path = ('rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day),)   #
    cur.execute(sql, day_path)          #
    day_hash = str(cur.fetchone()[0])   #
    month_path=('rootDir/'+str(temp_year)+'/'+str(temp_month),) #
    cur.execute(sql, month_path) #
    month_hash = str(cur.fetchone()[0]) #
    year_path=('rootDir/'+str(temp_year),)  #
    cur.execute(sql, year_path)
    year_hash = str(cur.fetchone()[0])
    root_path = ('rootDir',)                #
    cur.execute(sql, root_path)
    root_hash = str(cur.fetchone()[0])

    up_d = subprocess.check_output('/usr/local/bin/ipfs object patch '+ day_hash +' add-link ' + clip_name + ' ' + clip_hash, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #
    sql = 'UPDATE merkleDir SET hash=? WHERE path=?'      #
    update=(str(up_d), 'rootDir/'+str(temp_year)+'/'+str(temp_month)+'/'+str(temp_day)) #
    cur.execute(sql, update)
    conn.commit()
    up_m = subprocess.check_output('/usr/local/bin/ipfs object patch '+ month_hash +' add-link ' + str(temp_day) + ' ' + up_d, universal_newlines=True, stderr=subprocess.STDOUT, shell=True).strip() #
    update=(str(up_m), 'rootDir/'+str(temp_year)+'/'+str(temp_month))   #
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
