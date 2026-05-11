# Wedding Bot Project Structure

## 📁 File Overview

```
wedding-bot/
├── README.md                           # Quick start guide
├── DEPLOYMENT.md                       # Detailed CDK deployment guide
├── PROJECT_STRUCTURE.md               # This file
│
├── app.py                             # CDK app entry point
├── wedding_bot_stack.py               # CDK stack definition
├── cdk.json                           # CDK configuration
│
├── parse_schedule.py                  # Excel → JSON parser
├── schedule.json                      # Parsed schedule (generated)
│
├── dynamodb_schema.py                 # DynamoDB table management
├── telegram_bot.py                    # Telegram bot (local/polling)
├── lambda_reminder.py                 # Lambda: auto reminders
│
├── lambda/                            # Lambda deployment folder
│   ├── lambda_reminder.py            # Reminder function handler
│   ├── telegram_bot.py               # Bot for Lambda (if needed)
│   └── telegram_bot_handler.py       # Webhook handler
│
├── lambda_layer/                      # Lambda layer (generated)
│   └── python/lib/python3.9/site-packages/
│       ├── requests/
│       └── pytz/
│
├── requirements.txt                   # Python dependencies
├── requirements-cdk.txt              # CDK dependencies
│
├── deploy.sh                         # One-command deployment script
├── test_local.py                     # Local testing suite
│
├── .venv/                            # Virtual environment
├── .gitignore                        # Git ignore rules
└── cdk.out/                          # CDK synthesized output (generated)
```

## 📝 File Descriptions

### Core Files

#### `parse_schedule.py`
Parses the Excel wedding schedule and extracts tasks.

**Features:**
- Reads "Final Timeline" sheet
- Recognizes names: Mars, Dan, YT, Karina, Sandy, Rachel, Michelle, Rana, Robert, Dom, Sandeep, Ryan
- Merges consecutive identical tasks
- Outputs to `schedule.json`

**Usage:**
```bash
python parse_schedule.py
```

#### `schedule.json` (Generated)
JSON file containing all parsed tasks.

**Format:**
```json
[
  {
    "start_time": "05:30",
    "end_time": "05:35",
    "task": "Mars Make up to begin",
    "role": "bride",
    "people": ["Mars"]
  }
]
```

#### `dynamodb_schema.py`
Manages DynamoDB table creation and data upload.

**Usage:**
```bash
python dynamodb_schema.py create   # Create table
python dynamodb_schema.py upload   # Upload schedule
python dynamodb_schema.py list     # View tasks
```

**Table Schema:**
- **Primary Key**: `task_id` (String)
- **GSI 1**: `TimeIndex` - partition: `start_time`
- **GSI 2**: `RoleIndex` - partition: `role`, sort: `start_time`

#### `telegram_bot.py`
Main Telegram bot with polling (for local testing).

**Features:**
- `/start` - Show menu
- `/next15` - Next 15 minutes
- Interactive buttons
- Automatic reminders (when running locally)

**Usage:**
```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python telegram_bot.py
```

#### `lambda_reminder.py`
Lambda function that sends reminders 5 minutes before tasks.

**Trigger:** EventBridge (every 1 minute)

**Logic:**
1. Check current time (SGT)
2. Query tasks starting in 5 minutes
3. Send Telegram message with task details

### CDK Infrastructure

#### `app.py`
CDK application entry point.

**Configuration:**
- Region: `ap-southeast-1` (Singapore)
- Gets credentials from context or env vars

#### `wedding_bot_stack.py`
Defines all AWS resources.

**Resources Created:**
1. **DynamoDB Table** - `WeddingSchedule`
2. **Lambda Layer** - Python dependencies
3. **Lambda Function** - `wedding-reminder-bot`
4. **Lambda Function** - `wedding-query-bot` (optional)
5. **EventBridge Rule** - Trigger every minute
6. **IAM Roles** - Lambda execution + DynamoDB access
7. **CloudWatch Logs** - 7-day retention

#### `cdk.json`
CDK configuration and feature flags.

### Deployment

#### `deploy.sh`
One-command deployment script.

**Steps:**
1. Create/activate virtual environment
2. Install CDK dependencies
3. Install Lambda dependencies
4. Build Lambda layer
5. Bootstrap CDK (if needed)
6. Deploy stack

**Usage:**
```bash
./deploy.sh
```

#### `requirements.txt`
Python dependencies for Lambda and local bot:
- `openpyxl` - Excel parsing
- `boto3` - AWS SDK
- `python-telegram-bot` - Telegram API
- `pytz` - Timezone support
- `requests` - HTTP requests

#### `requirements-cdk.txt`
CDK dependencies:
- `aws-cdk-lib` - CDK framework
- `constructs` - CDK constructs

### Testing

#### `test_local.py`
Local testing suite.

**Tests:**
1. Excel parsing
2. Schedule data validation
3. Environment variables
4. Lambda dependencies
5. DynamoDB connection (optional)

**Usage:**
```bash
python test_local.py
```

### Lambda Deployment

#### `lambda/` Directory
Contains Lambda function code for deployment.

**Files:**
- `lambda_reminder.py` - Auto reminder handler
- `telegram_bot.py` - Bot code (if using Lambda)
- `telegram_bot_handler.py` - Webhook handler

#### `lambda_layer/` Directory
Lambda layer with Python packages.

**Built by:**
```bash
pip install requests pytz -t lambda_layer/python/lib/python3.9/site-packages/
```

## 🔄 Typical Workflow

### Initial Setup

1. **Parse Excel:**
   ```bash
   python parse_schedule.py
   ```

2. **Test Locally:**
   ```bash
   python test_local.py
   ```

3. **Deploy to AWS:**
   ```bash
   ./deploy.sh
   ```

4. **Upload Schedule:**
   ```bash
   python dynamodb_schema.py create
   python dynamodb_schema.py upload
   ```

### Update Schedule

1. **Update Excel file**

2. **Re-parse:**
   ```bash
   python parse_schedule.py
   ```

3. **Re-upload:**
   ```bash
   python dynamodb_schema.py upload
   ```

### Update Lambda Code

1. **Modify `lambda_reminder.py` or `telegram_bot.py`**

2. **Redeploy:**
   ```bash
   cdk deploy
   ```

### Cleanup

```bash
cdk destroy
```

## 🎯 Key Configuration Points

### Wedding Details
Edit in respective files:
- Date: `2026-05-09`
- Timezone: `Asia/Singapore` (SGT, UTC+8)
- Names: See `parse_schedule.py` `PEOPLE` dict

### Telegram
Set via environment variables:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### AWS
- Region: `ap-southeast-1` (Singapore)
- Table: `WeddingSchedule`
- Functions: `wedding-reminder-bot`, `wedding-query-bot`

### Reminder Timing
Edit in `lambda_reminder.py`:
```python
reminder_time = task_datetime - timedelta(minutes=5)
```

## 📊 Data Flow

```
Excel File
    ↓
parse_schedule.py
    ↓
schedule.json
    ↓
dynamodb_schema.py
    ↓
DynamoDB Table (WeddingSchedule)
    ↓
┌─────────────────────────┬─────────────────────┐
│                         │                     │
Lambda (Reminder)    Lambda (Query)      Local Bot
EventBridge ─→ Auto   User Query ─→   Polling ─→
│                         │                     │
└─────────────────────────┴─────────────────────┘
                    ↓
          Telegram Group Chat
```

## 🔐 Security Notes

- Never commit `.env` files
- Telegram tokens in environment variables only
- Lambda IAM roles: least privilege (DynamoDB read-only)
- CloudWatch logs: 7-day retention
- DynamoDB: encryption at rest enabled by default

## 💰 Cost Breakdown

All services stay within AWS Free Tier for a single-day event:

| Service | Free Tier | Expected Usage | Cost |
|---------|-----------|----------------|------|
| DynamoDB | 25 GB storage | ~100 items | $0 |
| Lambda | 1M requests/month | ~1,440/day | $0 |
| EventBridge | 14M events/month | ~1,440/day | $0 |
| CloudWatch Logs | 5 GB ingestion | ~10 MB | $0 |

**Total: ~$0.00** (essentially free!)

## 📞 Support

Issues? Check:
1. CloudWatch Logs: `/aws/lambda/wedding-reminder-bot`
2. DynamoDB Console: Verify data exists
3. EventBridge: Check rule is enabled
4. Telegram: Test bot token and chat ID
5. Local test: Run `python test_local.py`
