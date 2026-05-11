# Wedding Schedule Telegram Bot

A Telegram bot that sends automated reminders for wedding day schedules and allows querying upcoming tasks.

## Features

- 🔔 **Automatic Reminders**: Sends reminders 5 minutes before each scheduled task
- 📅 **Query Schedule**: Button to view tasks in the next 15 minutes
- 👥 **People Tracking**: Tracks which people are involved in each task
- ⏰ **Time-based Filtering**: View tasks by time ranges (15 mins, 1 hour, all day)

## Architecture

- **DynamoDB**: Stores all wedding schedule tasks
- **Lambda Function**: Triggered every minute by EventBridge to send reminders
- **Telegram Bot**: Provides interactive interface for querying schedule
- **Python**: All components written in Python 3.9+

## Quick Start

### 1. Install Prerequisites

- **AWS CDK CLI**: `npm install -g aws-cdk`
- **Python 3.9+**
- **AWS Account** with CLI configured

### 2. Create Telegram Bot

1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Save the bot token
4. Add the bot to your wedding group chat
5. Get the chat ID:
   ```bash
   # Send a message to your group, then run:
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates | jq
   # Look for "chat":{"id":<CHAT_ID>} in the response
   ```

### 3. Set Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

### 4. Deploy to AWS (One Command!)

```bash
./deploy.sh
```

This will:
- Install all dependencies
- Build Lambda layer
- Deploy complete infrastructure to AWS
- Create DynamoDB table, Lambda functions, EventBridge rules

### 5. Upload Wedding Schedule

```bash
source .venv/bin/activate

# Parse Excel and upload to DynamoDB
python parse_schedule.py
python dynamodb_schema.py create
python dynamodb_schema.py upload
```

### 6. Test the Bot

Open Telegram and try:
- `/start` - Show main menu
- `/next15` - Show next 15 minutes tasks

Done! 🎉

---

## Detailed Documentation

For detailed deployment instructions, troubleshooting, and advanced configuration:

📖 **[Read the Complete Deployment Guide](DEPLOYMENT.md)**

## Schedule Data Structure

Each task in DynamoDB contains:
- `task_id` (PK): Unique identifier
- `start_time`: Task start time (HH:MM)
- `end_time`: Task end time (HH:MM)
- `task`: Task description
- `role`: bride | groom | bridesmaid | groomsmen
- `people`: List of names involved
- `wedding_date`: 2026-05-09
- `timezone`: Asia/Singapore

## Usage

### Query Next 15 Minutes
Send `/next15` or click "Next 15 mins" button in the bot.

### Query Specific Times
The bot automatically sends reminders, but you can also:
- Click "Next Hour" to see upcoming tasks in the next 60 minutes
- Click "All Tasks Today" to see the complete schedule

### Reminders
The Lambda function runs every minute and automatically sends reminders to the group chat 5 minutes before each task starts.

## Wedding Details

- **Date**: May 9, 2026
- **Timezone**: Singapore Time (SGT, UTC+8)
- **Bride**: Mars
- **Groom**: Daniel (Dan)
- **Bridesmaids**: YT, Karina, Sandy, Rachel, Michelle
- **Groomsmen**: Rana, Robert, Dom, Sandeep, Ryan

## Troubleshooting

### Bot not responding
- Check if bot token is correct
- Ensure bot is added to the group chat
- Verify chat ID is correct

### Reminders not sending
- Check Lambda CloudWatch logs
- Verify EventBridge rule is enabled
- Ensure Lambda has DynamoDB read permissions
- Check if wedding date matches (reminders only sent on wedding day)

### DynamoDB errors
- Verify table exists: `aws dynamodb describe-table --table-name WeddingSchedule`
- Check IAM permissions for Lambda role

## Cost Estimate (AWS)

- **DynamoDB**: ~$0 (under free tier for 100 tasks)
- **Lambda**: ~$0 (under free tier, ~1440 invocations per day)
- **EventBridge**: ~$0 (under free tier)

**Total**: Essentially free for a one-day event!

## Future Enhancements

- [ ] Add command to query tasks by person name
- [ ] Send personalized reminders to individual bridesmaids/groomsmen
- [ ] Add ability to mark tasks as complete
- [ ] Post-wedding statistics and timeline review
- [ ] Photo upload feature for each task
