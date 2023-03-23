import requests
import argparse
import base64
import os
import json
import random
from requests.auth import HTTPBasicAuth
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--filename', nargs='+', help='Name(s) of the file(s) to encode')
parser.add_argument('--target-address', help='Bitcoin address to send the transaction to')
args = parser.parse_args()

# Bitcoin Core node connection
rpc_user = "rpc"
rpc_password = "rpc"
rpc_ip = "192.168.17.194"
rpc_port = 8332

cntrprty_url = "http://192.168.17.194:4000"
cntrprty_headers = {'content-type': 'application/json'}
cntrprty_auth = HTTPBasicAuth('rpc', 'rpc')

wallet_name = "stampmint"

log_file_path = "stamp_out.json"

def check_asset_availability(asset_name):
    payload = {
        "method": "get_asset_info",
        "params": {
            "assets": [asset_name]
        },
        "jsonrpc": "2.0",
        "id": 0
    }
    response = requests.post(cntrprty_url, data=json.dumps(payload), headers=cntrprty_headers, auth=cntrprty_auth)
    result = json.loads(response.text)
    # If the result is an empty list, the asset does not exist, and the function returns True
    # If the result contains any content, the asset exists, and the function returns False
    return len(result["result"]) == 0


def create_raw_issuance(source_address, asset_name, base64_data, transfer_address):
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
            "allow_unconfirmed_inputs": True,
            #"dust_return_pubkey": ":",
            "extended_tx_info": True
            # "multisig_dust_size": 7800, # default value of 7800
            # "fee": 111 # custom miner fee - default server chooses
            # "fee_per_kb": 111 # constant that the server uses when deciding on the dynamic fee
            # "fee_provided": 111 #  This differs from fee in that this is an upper bound value, which fee is an exact value
        },
        "jsonrpc": "2.0",
        "id": 0
    }
    # print("payload", payload, "\n") # debug

    # Send the API request
    response = requests.post(cntrprty_url, data=json.dumps(payload), headers=cntrprty_headers, auth=cntrprty_auth)
    result = json.loads(response.text)
    # print("RESULT:",result) # Debug
    try:
        raw_transaction = result['result']
    except KeyError:
        print(f"Error: {result['error']['message']}")
        return None

    return raw_transaction

def calculate_miner_fees(raw_transaction):
    decoded_transaction = get_rpc_connection(wallet_name).decoderawtransaction(raw_transaction)
    inputs_value = sum([txin['value'] for txin in decoded_transaction['vin']])
    outputs_value = sum([txout['value'] for txout in decoded_transaction['vout']])
    miner_fees = inputs_value - outputs_value
    return miner_fees

def decode_raw_transaction(raw_transaction):
    rpc_connection = get_rpc_connection(wallet_name)
    tx = rpc_connection.decoderawtransaction(raw_transaction)
    return tx

def generate_available_asset_name():
    max_asset_id = 2**64 - 1
    min_asset_id = 26**12 + 1
    asset_name = "A" + str(random.randint(min_asset_id - 8008, max_asset_id - 8008))
    while not check_asset_availability(asset_name):
        asset_name = "A" + str(random.randint(min_asset_id - 8008, max_asset_id - 8008))
    return asset_name

def get_rpc_connection(wallet_name=None):
    wallet_path = f"/wallet/{wallet_name}" if wallet_name else ""
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}{wallet_path}")

def get_utxos(address, min_conf=1, max_conf=9999999):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.listunspent(min_conf, max_conf, [address])

def sign_raw_transaction_with_wallet(raw_transaction):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.signrawtransactionwithwallet(raw_transaction)

def broadcast_signed_transaction(signed_transaction):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.sendrawtransaction(signed_transaction["hex"])

def get_fee_rate():
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.estimatesmartfee(2)["feerate"]

def generate_new_address():
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.getnewaddress()

def log_entry(target_address, filename, transaction_id,computed_fee, tx_fees_from_outputs, base64_size, asset_name, btc_trx_fees_from_issuance, transaction_size, current_fee_rate):
    log_entry = {
        "target_address": target_address,
        "filename": filename,
        "transaction_id": transaction_id,
        "current_fee_rate": current_fee_rate,
        "computed_fee": str(computed_fee),
        "tx_fees_from_outputs": str(tx_fees_from_outputs),
        "base64_size": base64_size,
        "transaction_size": transaction_size,
        "asset_name": asset_name,
        "btc_trx_fees_from_issuance": str(btc_trx_fees_from_issuance)
    }

    # If the log file exists, read its contents
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            log_data = json.load(log_file)
    else:
        log_data = []

    # Add the new entry to the log data
    log_data.append(log_entry)

    # Write the updated log data back to the file
    with open(log_file_path, "w") as log_file:
        json.dump(log_data, log_file, indent=4)


# Get fee rate (in BTC/kB)
current_fee_rate = get_fee_rate()
print("current fee rate:", current_fee_rate)

asset_name = generate_available_asset_name()
print("asset name:", asset_name) # debug

#source_address = generate_new_address()
#print(f"New address generated: {new_address}") # debug
source_address = "1GPfBjHemZayEHkPFuMTQsPUPDSdv86oHf" # stampmint
transfer_address = source_address # must be same as source address

# Read file and encode to base64, create transaction, sign it, broadcast it
if args.filename:
    for filename in args.filename:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                base64_data = base64.b64encode(f.read()).decode('utf-8')
                base64_size = len(base64_data)


                # print(f'Base64 encoded data for file {filename}: {base64_data}') # debug

                raw_transaction = create_raw_issuance(source_address, asset_name, base64_data, transfer_address)
                #print("raw_transaction: ", raw_transaction, "\n") # debug
                if raw_transaction is None:
                    print("Error creating raw transaction. Bye.")
                    exit()
                # else:
                #     print(raw_transaction["tx_hex"]) #debug
                btc_trx_fees_from_issuance = raw_transaction["btc_fee"]
                raw_transaction = raw_transaction["tx_hex"]
                
                # Get the transaction's size  -- should be able to skip the decoding piece and use data from the raw_transaction keys
                # tx_fees_from_outputs = calculate_miner_fees(raw_transaction)
                # print("tx fees from outputs", tx_fees_from_outputs)

                transaction_size = len(raw_transaction) // 2  # in bytes
                print("transaction size", transaction_size) # debug

                print("base64 size:", base64_size)
                # Calculate the transaction fee based on size and fee rate
                computed_fee = transaction_size * current_fee_rate / 1000  # in BTC

                print("computed fees", computed_fee) # Debug

                # Sign the transaction
                signed_transaction = sign_raw_transaction_with_wallet(raw_transaction)
                # Broadcast the signed transaction
                transaction_id = broadcast_signed_transaction(signed_transaction)
                print(f"Transaction ID: {transaction_id}")

                os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

                # now we need to send the transaction to args.target_address

                log_entry(args.target_address, filename, transaction_id, computed_fee, "0", base64_size, asset_name, btc_trx_fees_from_issuance, transaction_size, current_fee_rate)
        else:
            print(f"File not found: {filename}")
else:
    print('No filename specified.')


