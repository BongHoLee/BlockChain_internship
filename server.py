#-*- coding: utf-8 -*-
from flask import Flask
import os
import sys
from datetime import datetime
import time
import subprocess
import sqlite3
from web3 import Web3, HTTPProvider, IPCProvider
from queue import Queue

rpc_url = "http://192.168.1.2:8545"
w3 = Web3(HTTPProvider(rpc_url))

contract = w3.eth.contract(abi=[{'constant': False, 'inputs': [{'name': '_dbData', 'type': 'string'}], 'name': 'insertData', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getIndex', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getUser', 'outputs': [{'name': 'dbData', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}])

tx_receipt = w3.eth.getTransactionReceipt('0x6857f2bd85cea3cf5a0a84b80e1bea44d2fc660f5ba07a47e7d6808eab78aae9')
contract_address = tx_receipt['contractAddress']
contract_instance = contract(contract_address)

def blockChain() :
    i=0
    with open('block.txt', "w") as f :
        while contract_instance.call().getIndex() > i:
            #index = contract_instance.call().getIndex()
            data = contract_instance.call().getUser(i)
            f.write('\n\n')
            f.write(str(i))
            f.write(data)
            f.write("\n")
            i += 1


app = Flask(__name__)

@app.route("/")
def hello():
    with open('block.txt', "r") as f:
        data=f.read()
        print(data)
    return data

if __name__ == '__main__' :
    blockChain()
    app.run()
