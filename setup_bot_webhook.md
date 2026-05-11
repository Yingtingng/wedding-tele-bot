# Setup Telegram Bot Webhook on AWS

This allows the bot to respond to commands 24/7 without your laptop running.

## Architecture

Instead of polling (requires laptop running), use webhook mode:
```
Telegram → API Gateway → Lambda → Responds to commands
```

## Steps to Deploy

### 1. Update CDK Stack

Add this to `wedding_bot_stack.py`:

```python
# API Gateway for bot webhook
from aws_cdk import aws_apigateway as apigw

# Bot webhook Lambda
bot_webhook_function = lambda_.Function(
    self,
    "BotWebhookFunction",
    function_name="wedding-bot-webhook",
    runtime=lambda_.Runtime.PYTHON_3_9,
    handler="telegram_bot_handler.lambda_handler",
    code=lambda_.Code.from_asset("lambda"),
    timeout=Duration.seconds(10),
    memory_size=256,
    environment={
        "TELEGRAM_BOT_TOKEN": telegram_token,
        "TELEGRAM_CHAT_ID": chat_id,
        "DYNAMODB_TABLE": table.table_name,
    },
    layers=[lambda_layer],
)

table.grant_read_data(bot_webhook_function)

# API Gateway
api = apigw.RestApi(
    self,
    "BotWebhookApi",
    rest_api_name="wedding-bot-webhook",
    description="Webhook endpoint for Telegram bot"
)

webhook = api.root.add_resource("webhook")
webhook.add_method(
    "POST",
    apigw.LambdaIntegration(bot_webhook_function)
)

# Output the webhook URL
cdk.CfnOutput(
    self,
    "WebhookUrl",
    value=api.url + "webhook",
    description="Telegram webhook URL"
)
```

### 2. Deploy

```bash
cd /Users/yingting/Library/CloudStorage/OneDrive-amazon.com/dev/others/wedding-bot
cdk deploy
```

This outputs a webhook URL like:
```
https://abc123.execute-api.ap-southeast-1.amazonaws.com/prod/webhook
```

### 3. Register Webhook with Telegram

```bash
export WEBHOOK_URL="<your-api-gateway-url>/webhook"
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=$WEBHOOK_URL"
```

### 4. Test

Send `/start` or `/next15` in your Telegram group - the bot responds automatically!

## Pros & Cons

### Webhook (AWS Lambda)
✅ Runs 24/7 without laptop  
✅ No polling overhead  
✅ Instant responses  
✅ Free tier covers wedding day  
❌ Requires API Gateway setup  
❌ Need to register webhook  

### Local Bot (Laptop)
✅ Simple to run  
✅ Easy to debug  
❌ Needs laptop on  
❌ Must keep terminal open  

## Cost

API Gateway + Lambda for bot queries:
- ~100 messages on wedding day
- Free tier covers it
- **Cost: $0**

Total AWS cost for wedding: **$0** (all within free tier)

## Wedding Day Recommendation

**You don't need the query bot running for the wedding to work!**

The Lambda reminder function (already deployed) is the critical piece:
- Runs 24/7 automatically ✅
- Sends reminders without any action ✅
- No laptop needed ✅

The query bot is optional:
- Nice to have for checking schedule
- Can run locally when needed
- Or deploy webhook for 24/7 availability
