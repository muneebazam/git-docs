#!/bin/bash

echo "Copying python functions to deployment folder..."
mkdir deployment
cp publisher_lib.py deployment/
cp site_publisher.py deployment/
cd deployment

echo "Deploying site publisher lambda functions..."
pip install requests --target .
zip -r package.zip .
aws lambda update-function-code --function-name site-publisher --region us-east-1 --zip-file fileb://package.zip

echo "Done"