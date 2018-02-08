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
    temp_index = curs.fetchone()    #현재 DB에 저장된 마지막 열의 index를 가져온다.
    if temp_index is None :         #데이터베이스에 저장된 내용이 아무것도 없다면 실행
        f_values = contract_instance.call().getData(0)
        curs.execute("""INSERT INTO metaData VALUES(%s,%s,%s,%s,%s,%s)""", (0,f_values[1],f_values[2],f_values[3],f_values[4],f_values[5]))
        conn.commit()
        continue
    temp_index = temp_index[0]          #테이블의 index를 정수형으로 가져옴(튜플로 반환되기 때문)
    contract_index = int(contract_instance.call().getIndex())   #현재 컨트랙트에 저장된 마지막 배열의 index
    while contract_index > temp_index : #컨트랙트 배열의 index가 테이블의 index보다 크다면 컨트랙트에 저장된 데이터를 데이터베이스에 저장
        temp_index += 1
        contract_value = contract_instance.call().getData(temp_index)
        db_value = eval(contract_value)
        curs.execute("""INSERT INTO metaData VALUES(%s,%s,%s,%s,%s,%s)""", (temp_index, db_value[1], db_value[2], db_value[3], db_value[4], db_value[5]))
        conn.commit()
        print('inserted!')
    time.sleep(180)
