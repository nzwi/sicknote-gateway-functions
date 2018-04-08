##
# Title: Python functions to communicate with the sicknote smart contract hosted in the Blockchain
# Version: v00_01
# Author: Nzwisisa Chidembo <nzwisisa@gmail.com>
##

import os
from web3 import Web3, HTTPProvider, Account

"""
####################Sample requests######################
testEvent = {
    "request": {
        "type": "GetLastSickNote",
        "data": {
            "patientId": 00000000000
        }
    }
}

testEvent = {
    "request": {
        "type": "AddNote",
        "data": {
            "practiceNo": 000000000,
            "patientId": 0000000000,
            "sickDays": 0,
            "illnessDescription": "xxxxxxxxxxxx"
        }
    }
}

testEvent = {
    "request": {
        "type": "AddPatient",
        "data": {
            "practiceNo": 0000000000,
            "patientId": 0000000000000000,
            "firstName": "xxxxxxxxxxxxx",
            "lastName": "xxxxxxxxxxxx"
        }
    }
}

testEvent = {
    "request": {
        "type": "AddDoctor",
        "data": {
            "practiceNo": 000000,
            "firstName": "xxxxxxxxxxx",
            "lastName": "xxxxxxxxxx",
            "physicalAddress": "xxxxxxxxxxxx",
            "phoneNo": "0000000000000"
        }
    }
}

"""
###################Infura API, Contract, Wallet Settings#######################
settings = {
    "httpProvider": "",
    "contractAddress": "",
    "adminWalletAddress": "",
    "adminWalletPrivateKey": "",
    "chainId": 3,
    "gas": 2000000,
    "gasPrice": 10000000000
}

def addDoctorFunction(data,c,nonce):
    return c.functions.addDoctor(
        data['practiceNo'],
        data['firstName'],
        data['lastName'],
        data['physicalAddress'],
        data['phoneNo']
    ).buildTransaction({
        'chainId': settings['chainId'],
        'gas': settings['gas'],
        'gasPrice': settings['gasPrice'],
        'nonce': nonce
    })

def addPatientFunction(data,c,nonce):
    return c.functions.addPatient(
        data['practiceNo'],
        data['patientId'],
        data['firstName'],
        data['lastName']
    ).buildTransaction({
        'chainId': settings['chainId'],
        'gas': settings['gas'],
        'gasPrice': settings['gasPrice'],
        'nonce': nonce
    })

def addNoteFunction(data,c,nonce):
    return c.functions.addNote(
        data['practiceNo'],
        data['patientId'],
        data['sickDays'],
        data['illnessDescription']
    ).buildTransaction({
        'chainId': settings['chainId'],
        'gas': settings['gas'],
        'gasPrice': settings['gasPrice'],
        'nonce': nonce
    })

def buildBlockchainRequest(request,c,nonce):
    response = ''
    if request['type'] == 'AddDoctor':
        response = addDoctorFunction(request['data'],c,nonce)
    elif request['type'] == 'AddPatient':
        response = addPatientFunction(request['data'],c,nonce)
    elif request['type'] == 'AddNote':
        response = addNoteFunction(request['data'],c,nonce)
    else:
        response = 'err'
    return response

def buildResponse(msg):
    return {
        "response": {
            "type": msg,
            "data": {}
        }
    }

def buildSuccessResponse(tx_hash):
    return {
        "response": {
            "type": "success",
            "data": {
                "transactionHash": tx_hash
            }
        }
    }

def buildCallSuccessResponse(data):
    return {
        "response": {
            "type": "success",
            "data": {
                "practiceNo": data[0],
                "timeStamp": data[1],
                "sickDays": data[2],
                "illnessDescription": data[3]
            }
        }
    }

def lambda_handler(event, context):
    contract_abi = ''

    #You will need to read from your contract's ABI below
    with open('xxxxxxxxxxxxx.txt','r') as f:
        contract_abi = eval(f.read())

    infura_provider = HTTPProvider(settings['httpProvider'])
    web3 = Web3(infura_provider)

    address = settings['contractAddress']

    myContract = web3.eth.contract(
        address = address,
        abi = contract_abi
    )

    if event['request']['type'] == 'GetLastSickNote':
        res = myContract.functions.getLastSickNote(event['request']['data']['patientId']).call()
        return buildCallSuccessResponse(res)
    else:
        nonce = web3.eth.getTransactionCount(settings['adminWalletAddress'])

        txn = buildBlockchainRequest(event['request'],myContract, nonce)

        if txn == 'err':
            return buildResponse(txn)

        private_key = settings['adminWalletPrivateKey']

        signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)

        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

        return buildSuccessResponse(tx_hash)
