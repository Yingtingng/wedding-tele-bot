# CDK Deployment Guide

Complete guide to deploy the Wedding Reminder Bot using AWS CDK.

## Prerequisites

1. **AWS Account** with CLI configured
2. **Python 3.9+** installed
3. **Node.js 18+** (for CDK CLI)
4. **Telegram Bot** created via @BotFather

## Quick Start

### 1. Install CDK CLI

```bash
npm install -g aws-cdk
```

Verify installation:
```bash
cdk --version
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key, Secret Key, and set region to ap-southeast-1
```

### 3. Create Telegram Bot

1. Open Telegram and talk to [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Save the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Add bot to your wedding group chat
5. Get chat ID:
   ```bash
   # Send a test message to the group, then:
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" | jq
   # Look for "chat":{"id": -123456789}
   ```

### 4. Set Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"  # Include the negative sign if present
```

Or create a `.env` file:
```bash
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF

# Load it
source .env
```

### 5. Deploy Everything

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This script will:
- Create virtual environment
- Install dependencies
- Build Lambda layer with dependencies
- Bootstrap CDK (if needed)
- Deploy the stack to AWS

### 6. Upload Schedule to DynamoDB

```bash
# Activate virtual environment
source .venv/bin/activate

# Create and upload schedule
python dynamodb_schema.py create
python dynamodb_schema.py upload

# Verify
python dynamodb_schema.py list
```

### 7. Test the Bot

Open Telegram and test:
- `/start` - Show welcome message
- `/next15` - Show next 15 minutes tasks

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Install Dependencies

```bash
# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install CDK dependencies
pip install -r requirements-cdk.txt

# Install Lambda dependencies
pip install -r requirements.txt
```

### 2. Build Lambda Layer

```bash
mkdir -p lambda_layer/python/lib/python3.9/site-packages
pip install requests pytz -t lambda_layer/python/lib/python3.9/site-packages/
```

### 3. Bootstrap CDK

```bash
# Only needed once per AWS account and region
cdk bootstrap aws://YOUR_ACCOUNT_ID/ap-southeast-1
```

### 4. Deploy Stack

```bash
cdk deploy \
    -c telegram_token="$TELEGRAM_BOT_TOKEN" \
    -c chat_id="$TELEGRAM_CHAT_ID"
```

### 5. Upload Data

```bash
python dynamodb_schema.py create
python dynamodb_schema.py upload
```

## What Gets Deployed?

The CDK stack creates:

### 1. DynamoDB Table
- **Name**: `WeddingSchedule`
- **Billing**: Pay-per-request (on-demand)
- **Indexes**:
  - `TimeIndex` - Query by start_time
  - `RoleIndex` - Query by role and start_time

### 2. Lambda Function (Reminder)
- **Name**: `wedding-reminder-bot`
- **Runtime**: Python 3.9
- **Timeout**: 30 seconds
- **Trigger**: EventBridge rule (every 1 minute)
- **Purpose**: Send reminders 5 mins before tasks

### 3. Lambda Function (Query)
- **Name**: `wedding-query-bot`
- **Runtime**: Python 3.9
- **Timeout**: 60 seconds
- **Purpose**: Handle bot queries (can be extended to webhook)

### 4. EventBridge Rule
- **Schedule**: Every 1 minute
- **Target**: Reminder Lambda function

### 5. IAM Roles
- Lambda execution roles with DynamoDB read permissions

### 6. CloudWatch Logs
- Log groups with 7-day retention

## Cost Estimate

For a single wedding day (May 9, 2026):

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 100 items, on-demand | ~$0.00 (free tier) |
| Lambda | ~1,440 invocations/day | ~$0.00 (free tier) |
| EventBridge | ~1,440 events/day | ~$0.00 (free tier) |
| CloudWatch Logs | 7-day retention | ~$0.10 |
| **Total** | | **~$0.10** |

## Viewing Deployed Resources

### CloudFormation Stack
```bash
aws cloudformation describe-stacks --stack-name WeddingBotStack
```

### Lambda Functions
```bash
aws lambda list-functions --query 'Functions[?contains(FunctionName, `wedding`)]'
```

### DynamoDB Table
```bash
aws dynamodb describe-table --table-name WeddingSchedule
```

### EventBridge Rules
```bash
aws events list-rules --name-prefix wedding
```

## Testing

### Test Lambda Locally

```bash
# Test reminder function
python lambda/lambda_reminder.py

# Test query function  
python telegram_bot.py
```

### Test Lambda in AWS

```bash
# Invoke reminder lambda
aws lambda invoke \
    --function-name wedding-reminder-bot \
    --payload '{}' \
    response.json

cat response.json
```

### Check CloudWatch Logs

```bash
# Get latest log stream
aws logs describe-log-streams \
    --log-group-name /aws/lambda/wedding-reminder-bot \
    --order-by LastEventTime \
    --descending \
    --max-items 1

# View logs
aws logs tail /aws/lambda/wedding-reminder-bot --follow
```

## Troubleshooting

### Issue: CDK Bootstrap Fails

**Solution**: Ensure you have admin permissions in AWS account
```bash
aws sts get-caller-identity  # Verify your AWS identity
```

### Issue: Lambda Can't Access DynamoDB

**Solution**: Check IAM permissions
```bash
aws lambda get-policy --function-name wedding-reminder-bot
```

### Issue: No Reminders Being Sent

**Solution**: Check these:
1. Verify EventBridge rule is enabled
2. Check Lambda CloudWatch logs
3. Verify today is the wedding day (2026-05-09)
4. Test Lambda manually

### Issue: Bot Not Responding

**Solution**: 
1. Verify bot token is correct
2. Check if bot is in the group chat
3. Verify chat ID (include negative sign for groups)
4. Run bot locally to test: `python telegram_bot.py`

### Issue: Deployment Fails - Lambda Layer

**Solution**: Rebuild Lambda layer
```bash
rm -rf lambda_layer
mkdir -p lambda_layer/python/lib/python3.9/site-packages
pip install requests pytz -t lambda_layer/python/lib/python3.9/site-packages/
```

## Updating the Stack

To update after making changes:

```bash
# Update schedule
python parse_schedule.py
python dynamodb_schema.py upload

# Redeploy Lambda functions
cdk deploy
```

## Cleanup

To delete all resources after the wedding:

```bash
# Delete CloudFormation stack
cdk destroy

# Confirm deletion
# This will delete: DynamoDB table, Lambda functions, EventBridge rules, IAM roles, etc.
```

Or manually via console:
1. Go to CloudFormation console
2. Select `WeddingBotStack`
3. Click "Delete"

## Advanced Configuration

### Change Reminder Time

Edit `lambda/lambda_reminder.py`:
```python
# Change from 5 minutes to 10 minutes
reminder_time = task_datetime - timedelta(minutes=10)
```

Redeploy:
```bash
cdk deploy
```

### Add More Query Options

Edit `telegram_bot.py` to add custom query buttons or commands.

### Enable Webhook (Instead of Polling)

1. Create API Gateway
2. Point webhook to Lambda function
3. Register webhook with Telegram:
```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
    -d "url=https://your-api-gateway.amazonaws.com/prod/webhook"
```

## Security Best Practices

1. **Never commit tokens**: Use environment variables or AWS Secrets Manager
2. **Least privilege**: Lambda IAM roles only have DynamoDB read access
3. **Encryption**: DynamoDB encryption at rest is enabled by default
4. **Logs**: CloudWatch logs are retained for only 7 days to reduce costs

## Support

For issues:
1. Check CloudWatch logs
2. Review this troubleshooting guide
3. Test components individually (Lambda, DynamoDB, Bot)
