#!/usr/bin/env python3
"""
Telegram bot for wedding schedule reminders and queries
"""
import os
import logging
from datetime import datetime, timedelta
import boto3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import pytz

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TABLE_NAME = 'WeddingSchedule'
TIMEZONE = pytz.timezone('Asia/Singapore')
WEDDING_DATE = datetime(2026, 5, 9, tzinfo=TIMEZONE).date()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def get_tasks_in_timerange(start_time, end_time):
    """Get all tasks within a time range"""
    response = table.scan()
    items = response.get('Items', [])

    # Filter tasks by time range
    filtered_tasks = []
    for item in items:
        task_start = datetime.strptime(item['start_time'], '%H:%M').time()
        if start_time <= task_start < end_time:
            filtered_tasks.append(item)

    # Sort by start time
    filtered_tasks.sort(key=lambda x: x['start_time'])
    return filtered_tasks

def format_task_message(task):
    """Format a task into a readable message"""
    people_str = ', '.join(task['people'])
    role_emoji = {
        'bride': '❤️',
        'groom': '💙',
        'bridesmaid': '👭',
        'groomsmen': '👬'
    }

    emoji = role_emoji.get(task['role'], '📋')
    return (
        f"{emoji} *{task['role'].title()}* [{task['start_time']}-{task['end_time']}]\n"
        f"👥 {people_str}\n"
        f"📝 {task['task']}\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("📅 Next 15 mins", callback_data='next_15')],
        [InlineKeyboardButton("🕐 Next Hour", callback_data='next_60')],
        [InlineKeyboardButton("📋 All Tasks Today", callback_data='all_today')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '👰🤵 *Wedding Schedule Bot* 👰🤵\n\n'
        'Welcome! Use the buttons below to check the schedule:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def next_15_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tasks in the next 15 minutes"""
    now = datetime.now(TIMEZONE)
    start_time = now.time()
    end_time = (now + timedelta(minutes=15)).time()

    tasks = get_tasks_in_timerange(start_time, end_time)

    if not tasks:
        message = "📭 No tasks scheduled in the next 15 minutes!"
    else:
        message = f"📅 *Upcoming Tasks (Next 15 mins)*\n\n"
        for task in tasks:
            message += format_task_message(task) + "\n"

    await update.message.reply_text(message, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    now = datetime.now(TIMEZONE)

    if query.data == 'next_15':
        start_time = now.time()
        end_time = (now + timedelta(minutes=15)).time()
        title = "Next 15 minutes"
    elif query.data == 'next_60':
        start_time = now.time()
        end_time = (now + timedelta(minutes=60)).time()
        title = "Next hour"
    elif query.data == 'all_today':
        start_time = datetime.min.time()
        end_time = datetime.max.time()
        title = "All tasks today"
    else:
        await query.edit_message_text("Unknown command")
        return

    tasks = get_tasks_in_timerange(start_time, end_time)

    if not tasks:
        message = f"📭 No tasks scheduled for: {title}"
    else:
        message = f"📅 *{title}*\n\n"
        for task in tasks:
            message += format_task_message(task) + "\n"

    # Telegram message limit is 4096 characters
    if len(message) > 4000:
        message = message[:4000] + "\n\n... (message truncated)"

    await query.edit_message_text(message, parse_mode='Markdown')

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send reminder 5 minutes before a task"""
    job_data = context.job.data
    task = job_data['task']

    message = (
        f"⏰ *REMINDER* - Starting in 5 minutes!\n\n"
        f"{format_task_message(task)}"
    )

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode='Markdown'
    )

def schedule_all_reminders(application: Application):
    """Schedule reminders for all tasks"""
    now = datetime.now(TIMEZONE)
    response = table.scan()
    tasks = response.get('Items', [])

    logger.info(f"Scheduling reminders for {len(tasks)} tasks...")

    for task in tasks:
        task_start_str = task['start_time']
        task_start_time = datetime.strptime(task_start_str, '%H:%M').time()

        # Combine with wedding date
        task_datetime = datetime.combine(WEDDING_DATE, task_start_time)
        task_datetime = TIMEZONE.localize(task_datetime)

        # Schedule reminder 5 minutes before
        reminder_time = task_datetime - timedelta(minutes=5)

        if reminder_time > now:
            application.job_queue.run_once(
                send_reminder,
                when=reminder_time,
                data={'task': task},
                name=f"reminder_{task['task_id']}"
            )
            logger.info(f"Scheduled reminder for {task_start_str}: {task['task'][:50]}")

def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return

    if not CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID environment variable not set!")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("next15", next_15_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Schedule all reminders
    schedule_all_reminders(application)

    logger.info("Bot started successfully!")

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
