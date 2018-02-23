import time
import sys
from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_files

# Web3 setting

rpc_url = "http://192.168.1.2:8545"
w3 = Web3(HTTPProvider(rpc_url))

#compile
compiled_sol = compile_files(['metaData.sol','Metadata'])
contract_interface = compiled_sol['{}:{}'.format('metaData.sol','MetaData')]


contract = w3.eth.contract(abi=contract_interface['abi'],
                           bytecode=contract_interface['bin'],
                           bytecode_runtime=contract_interface['bin-runtime'])

print(contract_interface['abi'])
# Deploy
#while w3.eth.getTransactionReceipt(tx_hash) is None :
#    time.sleep(3)
#time.sleep(15)
while True :
    try :
        pat = w3.eth.getTransactionReceipt(tx_hash)
        break
    except :
        continue
#tx_receipt = w3.eth.getTransactionReceipt('0xcd578a06d584ef9a857db373f2079fb6fb59e0d439501fb88fb1af4ef3b3b3b4')
#contract_address = tx_receipt['contractAddress']
#contract_instance = w3.eth.contract(address=contract_address, abi=contract_interface['abi'])


print("tx_hash: {}".format(tx_hash))
print("Finish deploying")
