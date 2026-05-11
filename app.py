#!/usr/bin/env python3
"""
CDK app for Wedding Reminder Bot
"""
import os
from aws_cdk import App, Environment
from wedding_bot_stack import WeddingBotStack

app = App()

# Get configuration from context or environment
telegram_token = app.node.try_get_context("telegram_token") or os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = app.node.try_get_context("chat_id") or os.getenv("TELEGRAM_CHAT_ID")

if not telegram_token or not chat_id:
    print("WARNING: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set!")
    print("Set them via:")
    print("  - Environment variables")
    print("  - CDK context: cdk deploy -c telegram_token=xxx -c chat_id=yyy")

# Deploy to Singapore region (ap-southeast-1)
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region='ap-southeast-1'  # Singapore
)

WeddingBotStack(
    app,
    "WeddingBotStack",
    telegram_token=telegram_token,
    chat_id=chat_id,
    env=env,
    description="Wedding Schedule Reminder Bot with Telegram integration"
)

app.synth()
