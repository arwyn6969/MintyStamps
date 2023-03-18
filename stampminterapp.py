import os
import base64
import json
import requests
import time
from requests.auth import HTTPBasicAuth
import sys
import random
import qrcode
from PIL import Image


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

    # If the asset is not found, it's available
    return "error" in result and "Asset not found" in result["error"]


# Function to generate a QR code PNG file
def generate_qr_code_png(data, filename):
    img = qrcode.make(data)
    img.save(filename)


# Set the URL, headers, and authentication for the API request
url = "https://127.0.0.1:4001"
headers = {'content-type': 'application/json'}
auth = HTTPBasicAuth('rpc', 'rpc')

# Prompt the user for the transfer and source addresses
transfer_address = input("Enter the transfer address for the assets: ")
source_address = input("Enter the source address for the assets: ")

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

# Loop through each file in the IN directory and convert it to base64
total_size = 0
for file_name in files:
    with open(os.path.join(in_dir, file_name), 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')
        total_size += len(base64_data)

    # Generate a random asset name and check its availability
    asset_name = generate_asset_name()
    while not check_asset_availability(asset_name):
        asset_name = generate_asset_name()

    # Calculate the price for the issuance based on the size of the data
    price = total_size * 0.0001  # 0.0001 satoshi per byte
    commission = price * 0.2  # 20% commission
    price += commission

    # Create a payload with the base64-encoded data in the description field
    payload = {
        "method": "create_issuance",
        "params": {
            "source": source_address,
            "asset": asset_name,
            "quantity": 1,
            "divisible": False,
            "description": file_name + ": " + base64_data,
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
