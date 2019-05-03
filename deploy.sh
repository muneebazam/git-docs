#!/bin/bash

echo "Copying common library to each deployment folder..."
cp portal_common_lib.py external/
cp portal_common_lib.py internal/
cp portal_common_lib.py tardis_bot/

echo "Deploying external portal lambda functions..."
cd external 
pip install requests --target .
zip -r package.zip .
aws lambda update-function-code --function-name external-portal-wrapper --region us-east-1 --zip-file fileb://package.zip
aws lambda update-function-code --function-name external-portal-publisher --region us-east-1  --zip-file fileb://package.zip

echo "Deploying internal portal lambda functions..."
cd ../internal
pip install requests --target .
zip -r package.zip .
aws lambda update-function-code --function-name internal-portal-wrapper --region us-east-1 --zip-file fileb://package.zip
aws lambda update-function-code --function-name internal-portal-publisher --region us-east-1  --zip-file fileb://package.zip

echo "Deploying tardis bot lambda functions..."
cd ../tardis_bot
pip install requests --target .
zip -r package.zip .
aws lambda update-function-code --function-name tardis-command-controller --region us-east-1 --zip-file fileb://package.zip
aws lambda update-function-code --function-name tardis-event-controller --region us-east-1  --zip-file fileb://package.zip
aws lambda update-function-code --function-name tardis-interactive-controller --region us-east-1 --zip-file fileb://package.zip
aws lambda update-function-code --function-name tardis-portal-onboard --region us-east-1  --zip-file fileb://package.zip
aws lambda update-function-code --function-name tardis-portal-remove --region us-east-1 --zip-file fileb://package.zip

echo "Done"