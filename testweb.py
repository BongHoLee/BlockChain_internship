#-*- coding: utf-8 -*-
from flask import Flask
import os
import sys
from datetime import datetime
import time
import subprocess
import sqlite3
from web3 import Web3, HTTPProvider, IPCProvider

"""현재 컨트랙트 내의 배열에 저장된 데이터가 300개가 넘어서 출력하는데 시간이 좀 걸릴 수 있습니다."""
"""실행을 위해서 모듈 web3를 설치하셔야 합니다. pip install web3로 간단히 설치하실 수 있습니다."""
"""따로 컨트랙트 코드는 미리 컴파일을 한 뒤에 abi와 트랜잭션 주소만 추출해서 입력했습니다. """

def getTx():

	result = ""
	rpc_url = "http://203.255.251.45:8545"
	w3 = Web3(HTTPProvider(rpc_url))

	contract = w3.eth.contract(abi=[{'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getUser', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])

	tx_receipt = w3.eth.getTransactionReceipt('0x6857f2bd85cea3cf5a0a84b80e1bea44d2fc660f5ba07a47e7d6808eab78aae9')
	contract_address = tx_receipt['contractAddress']
	contract_instance = contract(contract_address)

	temp = contract_instance.call().getIndex() #컨트랙트에 저장된 마지막 배열의 index를 가져옵니다.
	i=0

	#컨트랙트의 배열 인덱스 0~temp에 저장된 값을 가져옵니다.
	while temp > i :

		result += str(i) + '\n\n'
		result += (contract_instance.call().getUser(i))
		result += "\n"

	    # print("index : {} ".format(i)) #컨트랙트 배열의 인덱스
	    # print("data value : {} ".format(contract_instance.call().getUser(i))) #컨트랙트 배열의 i인덱스를 갖는 데이터 출력
	    # print('\n')

		i += 1

	return result

app = Flask(__name__)

@app.route("/")
def hello():
	return getTx()


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1337)
