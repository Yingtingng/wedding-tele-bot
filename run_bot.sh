#!/bin/bash
# Script to run the Telegram bot locally

# Set environment variables (from Lambda config)
export TELEGRAM_BOT_TOKEN="8478729172:AAFI2rMP3pAS4lTHdLULy2WLmVBJePgtggE"
export TELEGRAM_CHAT_ID="-5173254200"

# Activate virtual environment
source .venv/bin/activate

echo "=========================================="
echo "Starting Wedding Bot..."
echo "=========================================="
echo ""
echo "Bot is now running!"
echo "Try these commands in Telegram:"
echo "  /start   - Show menu"
echo "  /next15  - Next 15 minutes"
echo "  /next60  - Next hour"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the simple bot (works with Python 3.14)
python simple_bot.py
