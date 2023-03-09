README
<b>THE BASIC<b>
script creates assets on the Counterparty platform with PNG image files as the asset description. The assets are issued to a specified transfer address.

Prerequisites
Python 3.6 or higher
Requests library: pip install requests
Counterparty account and API access credentials
Usage
Clone the repository
Set the user and 1234 to your Counterparty API access credentials
Run the script using the command python create_assets.py
Enter the transfer address for the assets when prompted
Ensure that all PNG image files are placed in the PNGIN directory located in the same directory as the script.
The script will loop through each PNG image file in the directory, encode the image in base64, and create an asset with the image as the description. The asset name will be the name of the PNG file (without the extension).
The newly created assets will be issued to the transfer address specified in step 4.
Note: The PNGIN directory must exist and contain PNG image files for the script to function properly.

Limitations
The script creates non-divisible assets with a quantity of 1 for each image file.
Only PNG image files are supported.
The script does not handle errors or exceptions gracefully.
References
Counterparty API documentation: https://counterparty.io/docs/api/
Requests library documentation: https://docs.python-requests.org/en/latest/


Counterparty Stamp Issuance Script
This Python script allows you to create new asset issuances on the Counterparty platform, each one representing a unique "stamp" image. The script takes a directory of PNG images, converts them to base64, and includes them as a description in the issuance transaction on the Counterparty platform. The resulting asset can be transferred to any Counterparty address.

Requirements
Python 3.x
requests library
Usage
Clone this repository to your local machine
Create a virtual environment for the project (optional, but recommended)
Install the requests library with pip install requests
Place the PNG images you want to use as "stamps" in the PNGIN directory
Run the script with python issuance.py
Enter the Counterparty address you want to transfer the assets to when prompted
Wait for the script to finish creating the issuances
The script will send one API request per PNG image to create an asset issuance on the Counterparty platform. Each issuance will have a quantity of 1 and a lock status of True, meaning it cannot be transferred until the lock status is released. The transfer destination address is set by the user at runtime.

If an API request fails, the script will automatically retry the request up to 5 times before skipping to the next PNG image. The script also includes a 1-second delay between API requests to avoid overwhelming the Counterparty API.

Note
The Counterparty platform requires a small amount of XCP (the native Counterparty currency) to create new assets. You will need to have XCP in your Counterparty address before running this script.
