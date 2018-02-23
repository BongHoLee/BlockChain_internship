#-*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
import time
import subprocess
import pymysql
from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_files

rpc_url = "http://192.168.1.2:8545"                         #Mac mini의 geth와 통신하기 위한 HTTPProvider
w3 = Web3(HTTPProvider(rpc_url))
contract = w3.eth.contract(abi=[{'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getData', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])

conn = pymysql.connect(host='localhost', user='root', password='111111', db='blockChain', charset='utf8')

curs = conn.cursor()



tx_receipt = w3.eth.getTransactionReceipt('0xd501b20ee29b361f7babde65bbc78a13b583e8936a09aa235cde71289c39ebdb')
contract_address = tx_receipt['contractAddress']
contract_instance = contract(contract_address)


while True :
    sql = 'SELECT _id FROM metaData ORDER BY _id DESC LIMIT 1;'
    curs.execute(sql)
    temp_index = curs.fetchone()    #Retrieves the index of the last column stored in the current DB.
    if temp_index is None :         #Execute if there is nothing stored in the database
        contract_value = contract_instance.call().getData(0)            #get metaData from smart contract with index 0
        f_values = eval(contract_value)                                 #transform metaData to insert Data Base
        curs.execute("""INSERT INTO metaData VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", (0,f_values[1],f_values[2],f_values[3],f_values[4],f_values[5],f_values[6],f_values[7]))
        conn.commit()
        continue
    temp_index = temp_index[0]          #Takes the index of the table as an integer (because it is returned as a tuple)
    contract_index = int(contract_instance.call().getIndex())   #The index of the last array stored in the current contract
    while contract_index > temp_index : #if the index of the contract array is larger than the index of the table, the data stored in the contract is stored in the database
        temp_index += 1                 #Increase the DB index by 1 (to increase the index of the contract array by 1)
        contract_value = contract_instance.call().getData(temp_index)   #Store metadata (string type) stored in contract
        db_value = eval(contract_value) #Retrieves contract values ​​stored as a String and separates them into eval () functions (separated by the attributes of each table)
        curs.execute("""INSERT INTO metaData VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", (temp_index, db_value[1], db_value[2], db_value[3], db_value[4], db_value[5], db_value[6], db_value[7]))#(분리된 값들을 각각 테이블에 넣어줌)
        conn.commit()
        print('inserted!')
    time.sleep(180)
