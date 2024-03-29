import os
import base64
import json
import requests
import time
import subprocess
from requests.auth import HTTPBasicAuth
import sys
import random
import qrcode
from PIL import Image
from bitcoinrpc.authproxy import AuthServiceProxy
#from bitcoinrpc.authproxy import AuthServiceProxy


# Function to generate a random asset name with the given format
def generate_asset_name():
    return "A" + str(random.randint(10**19, 10**20 - 1))


# Function to check if the asset name is available using the API
def check_asset_availability(asset_name):
    payload = {
        "method": "get_asset_info",
        "params": {
            "assets": [asset_name]
        },
        "jsonrpc": "2.0",
        "id": 0
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    result = json.loads(response.text)
    print(result)

    # If the result is an empty list, the asset does not exist, and the function returns True
    # If the result contains any content, the asset exists, and the function returns False
    return len(result["result"]) == 0


# Function to generate a QR code PNG file
def generate_qr_code_png(data, filename):
    img = qrcode.make(data)
    img.save(filename)


def choose_output(listunspent_output):
    # Find the unspent output with the highest amount
    max_amount = 0
    output = None
    for unspent in listunspent_output:
        if unspent["amount"] > max_amount:
            max_amount = unspent["amount"]
            output = unspent

    return output

def sign_transaction(raw_transaction, input_txid, input_vout, input_scriptPubKey, input_amount, rpc_connection):
    signed_transaction = rpc_connection.signrawtransactionwithwallet(raw_transaction, [{"txid":input_txid, "vout":input_vout, "scriptPubKey":input_scriptPubKey, "amount":input_amount}])
    print("PRINTING SIGNED TRX")
    print(signed_transaction)
    # Return the signed transaction string
    print("DONE PRINTING")
    return signed_transaction["hex"]

#def sign_transaction(raw_transaction, input_txid, input_vout, input_scriptPubKey, input_amount):
#    signrawtransaction = subprocess.run(['fednode', 'exec', 'bitcoin', 'bitcoin-cli', 'signrawtransactionwithwallet', raw_transaction, '[{"txid":"' + input_txid + '","vout":' + str(input_vout) + ',"scriptPubKey":"' + input_scriptPubKey + '","amount":' + str(input_amount) + '}]'], stdout=subprocess.PIPE)
#    signed_transaction = signrawtransaction.stdout.decode('utf-8')
#    print(signed_transaction)
#    # Return the signed transaction string
#    return signed_transaction


# Set the URL, headers, and authentication for the API request
url = "http://127.0.0.1:4000"
headers = {'content-type': 'application/json'}
auth = HTTPBasicAuth('rpc', 'rpc')


rpc_connection = AuthServiceProxy("http://rpc:rpc@127.0.0.1:8332")


# Prompt the user for the transfer and source addresses
transfer_address = "1GPfBjHemZayEHkPFuMTQsPUPDSdv86oHf" 
source_address = "1GPfBjHemZayEHkPFuMTQsPUPDSdv86oHf"
#transfer_address = input("Enter the transfer address for the assets: ")
#source_address = input("Enter the source address for the assets: ")

# Get the full path to the IN directory
in_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "IN")

# Check if IN directory exists
if not os.path.exists(in_dir):
    print("IN directory not found.")
    sys.exit()

# Get list of files in the IN directory
files = [f for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]

if not files:
    print("No files found in IN directory.")
    sys.exit()



command = "fednode exec bitcoin bitcoin-cli getwalletinfo"
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
output = result.stdout.decode('utf-8')
print(output)
wallet_info = json.loads(output)
if "walletname" in wallet_info:
    print("Wallet is loaded.")
else:
    print("Wallet is not loaded.")
    command = "fednode exec bitcoin bitcoin-cli loadwallet 'stampmint'"
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout = result.stdout.decode('utf-8')
    stderr = result.stderr.decode('utf-8')
    print(stdout)

# Loop through each file in the IN directory and convert it to base64
total_size = 0
for file_name in files:
    with open(os.path.join(in_dir, file_name), 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')
        total_size += len(base64_data)

    # Generate a random asset name and check its availability
    asset_name = generate_asset_name()
    asset_name = "A303030303030303030"
    print(asset_name)
    while not check_asset_availability(asset_name):
        asset_name = generate_asset_name()
    print("past asset check - using asset_name",asset_name) # Debug
    asset_name="A7739951851191313000"
#    issuance --source=1MZUaVy6y7vmwh2MqMKTFy2JiqXteyevpN --quantity=1 --asset=A7739951851191313000

    # Calculate the price for the issuance based on the size of the data
    price = total_size * 0.0001  # 0.0001 satoshi per byte
    commission = price * 0.2  # 20% commission
    price += commission
    print("Price:", price)
    # Create a payload with the base64-encoded data in the description field
    payload = {
        "method": "create_issuance",
        "params": {
            "source": source_address,
            "asset": asset_name,
            "quantity": 1,
            "divisible": False,
            "description": "stamp:" + base64_data,
            "lock": True,
            "transfer_destination": transfer_address,
            "reset": False,
            "allow_unconfirmed_inputs": True
        },
        "jsonrpc": "2.0",
        "id": 0
    }

       # Send the API request
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    result = json.loads(response.text)
    print("RESULT OF ISSUANVE", result)
    #raw_transaction = result['result']
    #print(raw_transaction)


    # Get the list of unspent outputs
    listunspent = subprocess.run(['fednode', 'exec', 'bitcoin', 'bitcoin-cli', 'listunspent'], stdout=subprocess.PIPE)
    listunspent_output = json.loads(listunspent.stdout.decode('utf-8'))
    print(listunspent_output)
    # Choose the unspent output to use for signing
    output = choose_output(listunspent_output)
    input_txid = output["txid"]
    input_vout = output["vout"]
    input_scriptPubKey = output["scriptPubKey"]
    input_amount = output["amount"]

    # Sign the raw transaction
    signed_transaction = sign_transaction(raw_transaction, input_txid, input_vout, input_scriptPubKey, input_amount, rpc_connection)
    #output = json.loads(signed_transaction)
    #txid = output["txid"]
    #print(txid)

    #Broadcast the signed transaction
    #broadcast = subprocess.run(['bitcoin-cli', 'sendrawtransaction', signed_transaction], stdout=subprocess.PIPE)
    #broadcast_output = broadcast.stdout.decode('utf-8')

    print("Signed transaction: ", signed_transaction)
    #print("Transaction broadcast output: ", broadcast_output)

