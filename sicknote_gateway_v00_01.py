import os
from web3 import Web3, HTTPProvider, Account

"""
testEvent = {
    "request": {
        "type": "GetLastSickNote",
        "data": {
            "patientId": 8410285963180
        }
    }
}

testEvent = {
    "request": {
        "type": "AddNote",
        "data": {
            "practiceNo": 667788,
            "patientId": 8410285963180,
            "sickDays": 2,
            "illnessDescription": "Toe hurting"
        }
    }
}

testEvent = {
    "request": {
        "type": "AddPatient",
        "data": {
            "practiceNo": 667788,
            "patientId": 8410285963180,
            "firstName": "Goodluck",
            "lastName": "Jonathan"
        }
    }
}

testEvent = {
    "request": {
        "type": "AddDoctor",
        "data": {
            "practiceNo": 667788,
            "firstName": "Pinky",
            "lastName": "Zulu",
            "physicalAddress": "3 Pine, Ferndale, Randburg, 2655",
            "phoneNo": "0725552398"
        }
    }
}

settings = {
    "httpProvider": os.environ['httpProvider'],
    "contractAddress": os.environ['contractAddress'],
    "adminWalletAddress": os.environ['adminWalletAddress'],
    "adminWalletPrivateKey": os.environ['adminWalletPrivateKey'],
    "chainId": os.environ['chainId'],
    "gas": os.environ['gas'],
    "gasPrice": os.environ['gasPrice']
}
"""
settings = {
    "httpProvider": "https://ropsten.infura.io/v3mvvmXsrXTl0DxgtPjN",
    "contractAddress": "0x46817097CaD67011b7749D64325A802b8D7F730D",
    "adminWalletAddress": "0xc173354F5Fbf628ff3AfBB8Be46F042015A7035c",
    "adminWalletPrivateKey": "80a15098a285927dfe436e675a6920c8de5000513ba6f5d34d1c26afbc88f2b7",
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

    with open('contract_abi.txt','r') as f:
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

#print(lambda_handler(testEvent,[]))
