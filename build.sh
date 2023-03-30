#!/bin/bash

mkdir lambda_package
cd lambda_package
ln -s ../lambda_function.py ./lambda_function.py
ln -s ../requirements.txt ./requirements.txt
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cp -r venv/lib/python3.9/site-packages/. .
# assuming python3.9
# cp -r venv/lib/python$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")/site-packages/. .
zip -r lambda_package.zip .
mv lambda_package.zip ..
cd ..
rm -rvf lambda_package
