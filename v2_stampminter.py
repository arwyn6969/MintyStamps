import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Configure your Bitcoin Core node connection
rpc_user = "rpc"
rpc_password = "rpc"
rpc_ip = "127.0.0.1"
rpc_port = 8332

wallet_name = "stampmint"

def get_rpc_connection(wallet_name=None):
    wallet_path = f"/wallet/{wallet_name}" if wallet_name else ""
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}{wallet_path}")

#def get_rpc_connection():
#    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}")

def get_utxos(address, min_conf=1, max_conf=9999999):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.listunspent(min_conf, max_conf, [address])

def sign_raw_transaction_with_wallet(raw_transaction):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.signrawtransactionwithwallet(raw_transaction)

def send_raw_transaction(signed_transaction):
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.sendrawtransaction(signed_transaction["hex"])

def get_fee_rate():
    rpc_connection = get_rpc_connection(wallet_name)
    return rpc_connection.estimatesmartfee(2)["feerate"]

# Get fee rate (in BTC/kB)
fee_rate = get_fee_rate()

# You should have the raw transaction hex in the 'raw_transaction' variable
raw_transaction = "0100000001a1a6e8b192941539076f862200da95d50e0cb9f1946547055f2d65bbc316cc31010000001976a914a8d2e9c3426d63b7f0b1dc06c26869e7843fe58f88acffffffff0922020000000000001976a914a8d2e9c3426d63b7f0b1dc06c26869e7843fe58f88ac781e00000000000069512103c35addd38e6ece83b3ade931aba6c84dac6b1018786d56f7ddd61cefa91229f02103b4a26582d22c807c117a00abb4dcf34e5f6053c05cbb780531ce3e43bd09203d2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512103c35addd38e6ece83b3f8c3193fccd7ee434251593c352794ee9c5dafe82010732103e48d58eefe2fb87e394071a1b2ffd52431576aa120c5203428fa3957ae1975df2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512103c35addd38e6ece83b3ddec3930ffcd9c44283f6e1e5e6fdcbfe353adc8551219210396887a8eff51f060196260a19fd4cc5e765142cf65df242c57913e43bd0a212d2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512103c35addd38e6ece83b3d2ee1d2fc3c5c0743b224a2b3c61b290967bab9952094d2102a28263ce9422b840015a049087d7d4796f637dd84d835f7033c63d4a867f2f7e2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512102c35addd38e6ece83b3edc70835c2cdd8676c7f4c103939859c9d298c9b322ee72102b09b418aea4c9149735e62b39ed0ac6574565ef87ec5573734cf15699b3114ec2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512103c35addd38e6ece83b3ebc03133e3fbfd46305b512b277db696926b8cc054310f2102acba62cfe912a3571b4079b690e3a8392d6047a5409c7e0628ff2846cb316cea2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae781e00000000000069512102d25addd38e6ece83b3d1a93431c5f1c05a2c78544b2c39afec92799cc4201c9c2102948e54fdd73c96581078618db0f89c0f1e21128e0fee104064a97f02fc4b473d2103c067d3d03af257df24cab4f26183e85a3619b796dad50302f5754f2f6fb8166c53ae084f0600000000001976a914a8d2e9c3426d63b7f0b1dc06c26869e7843fe58f88ac00000000" 

# Get the transaction's size
decoded_transaction = get_rpc_connection(wallet_name).decoderawtransaction(raw_transaction)
transaction_size = len(raw_transaction) // 2  # in bytes

print("decoded trx:", decoded_transaction)

# Calculate the transaction fee based on size and fee rate
fee = transaction_size * fee_rate / 1000  # in BTC

print(fee) # Debug
# If you want to modify the transaction to include the fee, you can do that here.
# You'll need to calculate the new output amounts and create a new raw transaction.

# Sign the transaction
signed_transaction = sign_raw_transaction_with_wallet(raw_transaction)
print("signed trx: ", signed_transaction)
# Broadcast the signed transaction
transaction_id = send_raw_transaction(signed_transaction)
print(f"Transaction ID: {transaction_id}")

