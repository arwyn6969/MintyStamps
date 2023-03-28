import requests
import base64
import os
import time
import json
import random
from requests.auth import HTTPBasicAuth
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging
import boto3
from io import BytesIO

# Bitcoin Core node connection
rpc_user = os.environ["rpc_user"]
rpc_password = os.environ["rpc_password"]
rpc_ip = os.environ["rpc_ip"]
rpc_port = os.environ["rpc_port"]
cntrprty_url = os.environ["cntrprty_url"]
cntrprty_headers = {'content-type': 'application/json'}
cntrprty_auth = HTTPBasicAuth('rpc', 'rpc')
wallet_name = os.environ["wallet_name"]
log_file_path = "stamp_out.json"
total_fees = 0
aws_s3_bucketname = os.environ.get('aws_s3_bucketname', "stampchain.io")
aws_secret_access_key = os.environ.get('aws_secret_access_key')
aws_access_key_id = os.environ.get('aws_access_key_id')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
    )

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def upload_file_to_s3(file_obj_or_path, bucket_name, s3_file_path, s3_client, diskless=False):
    try:
        if diskless:
            s3_client.upload_fileobj(file_obj_or_path, bucket_name, s3_file_path)
        else:
            s3_client.upload_file(file_obj_or_path, bucket_name, s3_file_path)
    except Exception as e:
        print(f"failure uploading to aws {e}")

def get_rpc_connection(wallet_name=None):
    wallet_path = f"/wallet/{wallet_name}" if wallet_name else ""
    return AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}{wallet_path}")


def get_fee_rate(retries=3, backoff_factor=2):
    rpc_connection = get_rpc_connection(wallet_name)
    
    for i in range(retries):
        try:
            return rpc_connection.estimatesmartfee(1)["feerate"]
        except Exception as e:
            if i == retries - 1:
                logger.error(f"Failed to get fee rate after {retries} attempts. Error: {e}")
                raise
            else:
                wait_time = backoff_factor * (2 ** i)
                logger.warning(f"Attempt {i + 1}: Failed to get fee rate. Retrying in {wait_time} seconds. Error: {e}")
                time.sleep(wait_time)


def generate_new_address(retries=3, backoff_factor=2):
    rpc_connection = get_rpc_connection(wallet_name)

    for i in range(retries):
        try:
            return rpc_connection.getnewaddress()
        except Exception as e:
            if i == retries - 1:
                logger.error(f"Failed to generate new address after {retries} attempts. Error: {e}")
                raise
            else:
                wait_time = backoff_factor * (2 ** i)
                logger.warning(f"Attempt {i + 1}: Failed to generate new address. Retrying in {wait_time} seconds. Error: {e}")
                time.sleep(wait_time)


def is_base64_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string)
        # supported foromats for this PIL method
        # ".bmp, .dib, .gif, .tif, .tiff, .jfif, .jpe, .jpg, .jpeg, .pbm, .pgm, .ppm, .pnm, .png, .apng"
        # image = Image.open(io.BytesIO(image_data)) # requires PILLOW
        # image.verify()
        return True
    except Exception as e:
        print(f"Invalid base64 image string: {e}")
        print(base64_string)
        return False


#source_address = generate_new_address()
#print(f"New address generated: {new_address}") # debug
source_address = "1GPfBjHemZayEHkPFuMTQsPUPDSdv86oHf" # stampmint
# transfer_address = source_address 


def lambda_handler(event, context):
    logger.info("Lambda function started")
    
    # Get fee rate (in BTC/kB)
    logger.info("Getting fee rate...")
    current_fee_rate = get_fee_rate()
    logger.info(f"Current fee rate: {current_fee_rate}")

    source_address = "1GPfBjHemZayEHkPFuMTQsPUPDSdv86oHf"  # stampmint
    logger.info(f"Source address: {source_address}")

    file_content = event.get('image', None)
    target_address = event.get('address', None)

    transfer_address = target_address

    if file_content:
        processed_files = []
        filename = file_content

        if is_base64_image(file_content):
            base64_data = file_content
            base64_size = len(base64_data)
            logger.info(f"Generating new address...")
            send_to_address = generate_new_address()
            logger.info(f"Generated new address: {send_to_address}")
            logger.info(f"Base64 size: {base64_size}")
            computed_fee = ( base64_size * 3 ) * current_fee_rate 

            logger.info(f"Computed fees: {computed_fee}")

        processed_files.append({
            "filename": filename,
            "computed_fee": str(computed_fee),
            "current_fee_rate": str(current_fee_rate),
            'base64_data': base64_data,
            "transfer_address": transfer_address,
            "send_to_address": send_to_address,
            "base64_size": base64_size
        })

    output = processed_files
    stamp_data_file_obj = io.BytesIO(json.dumps(processed_files).encode())

    # Format the json_output variable
    json_output = f"{processed_files[0]['send_to_address']}.json"

    upload_file_to_s3(stamp_data_file_obj, aws_s3_bucketname, json_output, s3_client, diskless=True)

    logger.info("Lambda function finished")
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(output)
    }
