#!/bin/bash
set -e

echo "======================================"
echo "Wedding Bot CDK Deployment Script"
echo "======================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install CDK dependencies
echo ""
echo "Installing CDK dependencies..."
pip install -r requirements-cdk.txt

# Install Lambda dependencies
echo ""
echo "Installing Lambda dependencies..."
pip install -r requirements.txt

# Build Lambda layer
echo ""
echo "Building Lambda layer..."
mkdir -p lambda_layer/python/lib/python3.9/site-packages
pip install requests pytz -t lambda_layer/python/lib/python3.9/site-packages/

# Check for environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo ""
    echo "WARNING: TELEGRAM_BOT_TOKEN is not set!"
    read -p "Enter your Telegram Bot Token: " TELEGRAM_BOT_TOKEN
    export TELEGRAM_BOT_TOKEN
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo ""
    echo "WARNING: TELEGRAM_CHAT_ID is not set!"
    read -p "Enter your Telegram Chat ID: " TELEGRAM_CHAT_ID
    export TELEGRAM_CHAT_ID
fi

# Bootstrap CDK (only needed once per account/region)
echo ""
echo "Bootstrapping CDK (if needed)..."
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/ap-southeast-1

# Synthesize CloudFormation template
echo ""
echo "Synthesizing CDK stack..."
cdk synth

# Deploy
echo ""
echo "Deploying CDK stack..."
cdk deploy \
    -c telegram_token="$TELEGRAM_BOT_TOKEN" \
    -c chat_id="$TELEGRAM_CHAT_ID" \
    --require-approval never

echo ""
echo "======================================"
echo "Deployment complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Run: python dynamodb_schema.py create"
echo "2. Run: python dynamodb_schema.py upload"
echo "3. Test the bot in Telegram!"
echo ""
