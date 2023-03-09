README for Counterparty Asset Creation Scripts

This repository contains two Python scripts for creating assets on the Counterparty platform using PNG image files as asset descriptions. The Basic script creates non-divisible assets with a quantity of 1 for each image file and issues them to a specified transfer address. The Stamp Issuance script creates unique asset issuances for each PNG image in a directory, with a quantity of 1 and a lock status of True. These assets can be transferred to any Counterparty address.

Prerequisites

Python 3.6 or higher
Requests library: pip install requests
Counterparty account and API access credentials
Usage

Clone the repository
Set your Counterparty API access credentials in the scripts:
For the Basic script, set USER and PASSWORD variables in create_assets.py
For the Stamp Issuance script, set API_USER and API_PASSWORD variables in issuance.py
Place PNG image files in the PNGIN directory located in the same directory as the scripts
Run the script using the command python create_assets.py or python issuance.py
Follow the prompts to enter the transfer address (Basic) or destination address (Stamp Issuance) for the assets
The scripts will loop through each PNG image file in the directory, encode the image in base64, and create an asset with the image as the description. For the Basic script, the asset name will be the name of the PNG file (without the extension).
The newly created assets will be issued to the transfer address or destination address specified in step 5.
Limitations

The Basic script creates non-divisible assets with a quantity of 1 for each image file. Only PNG image files are supported. The script does not handle errors or exceptions gracefully.
The Stamp Issuance script creates unique asset issuances for each PNG image in the PNGIN directory, with a quantity of 1 and a lock status of True. The script retries failed API requests up to 5 times and includes a 1-second delay between requests to avoid overwhelming the Counterparty API.
References

Counterparty API documentation: https://counterparty.io/docs/api/
Requests library documentation: https://docs.python-requests.org/en/latest/
