# 🚀 Quick Start Guide - Wedding Bot

Complete setup in 5 steps!

## ✅ Prerequisites Checklist

- [ ] AWS Account with CLI configured
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed (for CDK)
- [ ] Telegram account

## 📱 Step 1: Create Telegram Bot (5 mins)

1. Open Telegram → search for **@BotFather**
2. Send `/newbot`
3. Follow prompts to name your bot
4. **Save the token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Create a group chat for the wedding party
6. Add your bot to the group
7. Get chat ID:
   ```bash
   # Send any message to the group first, then:
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" | jq
   ```
   Look for: `"chat":{"id": -123456789}` (include the minus sign!)

## 🔧 Step 2: Install CDK (2 mins)

```bash
# Install CDK globally
npm install -g aws-cdk

# Verify
cdk --version
```

## 🔐 Step 3: Configure AWS (2 mins)

```bash
# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (ap-southeast-1), Output format (json)

# Verify
aws sts get-caller-identity
```

## 🎯 Step 4: Set Environment Variables (1 min)

```bash
# Set these in your terminal
export TELEGRAM_BOT_TOKEN="paste_your_token_here"
export TELEGRAM_CHAT_ID="paste_your_chat_id_here"

# Or create .env file
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF

# Load it
source .env
```

## 🚀 Step 5: Deploy Everything (5 mins)

```bash
# Navigate to project
cd wedding-bot

# Make deploy script executable
chmod +x deploy.sh

# Deploy! (This does everything)
./deploy.sh
```

The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Build Lambda layer
- ✅ Bootstrap CDK
- ✅ Deploy complete stack

## 📊 Step 6: Upload Schedule (2 mins)

```bash
# Activate virtual environment
source .venv/bin/activate

# Parse Excel file
python parse_schedule.py

# Create DynamoDB table
python dynamodb_schema.py create

# Upload schedule
python dynamodb_schema.py upload

# Verify
python dynamodb_schema.py list
```

## ✨ Step 7: Test! (1 min)

Open Telegram and try:
- `/start` → See welcome message
- `/next15` → View next 15 minutes
- Click buttons to explore schedule

**That's it!** 🎉

---

## 📝 Common Commands

### Check Deployment Status
```bash
aws cloudformation describe-stacks --stack-name WeddingBotStack
```

### View Lambda Logs
```bash
aws logs tail /aws/lambda/wedding-reminder-bot --follow
```

### Test Lambda Manually
```bash
aws lambda invoke \
    --function-name wedding-reminder-bot \
    --payload '{}' \
    response.json && cat response.json
```

### Update Schedule
```bash
# After updating Excel file
python parse_schedule.py
python dynamodb_schema.py upload
```

### Redeploy Code Changes
```bash
cdk deploy
```

### Run Local Tests
```bash
python test_local.py
```

### Cleanup (After Wedding)
```bash
cdk destroy
```

---

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Test bot locally
python telegram_bot.py
```

### Lambda not sending reminders?
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/wedding-reminder-bot --follow

# Verify EventBridge rule
aws events list-rules --query 'Rules[?contains(Name, `wedding`)]'

# Note: Reminders only sent on wedding day (2026-05-09)!
```

### DynamoDB errors?
```bash
# Check table exists
aws dynamodb describe-table --table-name WeddingSchedule

# Count items
aws dynamodb scan --table-name WeddingSchedule --select "COUNT"
```

### CDK deployment fails?
```bash
# Check AWS credentials
aws sts get-caller-identity

# Re-bootstrap
cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/ap-southeast-1

# Try again
./deploy.sh
```

---

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome menu with buttons |
| `/next15` | Show tasks in next 15 minutes |

**Buttons:**
- 📅 Next 15 mins
- 🕐 Next Hour  
- 📋 All Tasks Today

---

## 🎯 What Happens on Wedding Day?

**May 9, 2026** at **05:30 SGT**:

1. Lambda runs every minute (via EventBridge)
2. Checks for tasks starting in 5 minutes
3. Sends reminder to Telegram group:
   ```
   ⏰ REMINDER - Starting in 5 minutes!
   
   ❤️ Bride [05:35-05:40]
   👥 Mars
   📝 Make up to begin
   ```
4. Repeats for every task throughout the day!

---

## 📞 Need Help?

1. **Read full guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Check structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. **Run tests**: `python test_local.py`
4. **Check logs**: CloudWatch Logs console

---

## 💡 Pro Tips

1. **Test before wedding day**: Change date in code to test reminders
2. **Backup Excel file**: Keep original safe
3. **Monitor costs**: Should be $0 but check AWS billing
4. **Post-wedding**: Run `cdk destroy` to clean up resources
5. **Customize reminders**: Edit `lambda_reminder.py` to change timing or format

---

## 🎊 Wedding Day Checklist

- [ ] Bot deployed and tested
- [ ] All tasks uploaded to DynamoDB
- [ ] EventBridge rule enabled
- [ ] Bot added to Telegram group
- [ ] All bridal party members in group
- [ ] Test reminder sent successfully
- [ ] Phone charged and notifications on!

**Have a wonderful wedding! 🎉👰🤵**
