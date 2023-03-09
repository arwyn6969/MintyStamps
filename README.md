README
This script creates assets on the Counterparty platform with PNG image files as the asset description. The assets are issued to a specified transfer address.

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
