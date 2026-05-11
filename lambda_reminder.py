#!/usr/bin/env python3
"""
AWS Lambda function to send reminders 5 minutes before tasks
Triggered by EventBridge every minute
"""
import os
import json
import logging
from datetime import datetime, timedelta
import boto3
import requests
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TABLE_NAME = os.getenv('DYNAMODB_TABLE', 'WeddingSchedule')
TIMEZONE = pytz.timezone('Asia/Singapore')
WEDDING_DATE = datetime(2026, 5, 9, tzinfo=TIMEZONE).date()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

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

def send_telegram_message(message):
    """Send message to Telegram group"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent successfully: {message[:50]}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

def get_tasks_to_remind():
    """Get tasks that need reminders in the next minute"""
    now = datetime.now(TIMEZONE)
    current_date = now.date()

    # Only send reminders on wedding day
    if current_date != WEDDING_DATE:
        logger.info(f"Not wedding day yet. Today: {current_date}, Wedding: {WEDDING_DATE}")
        return []

    # Get all tasks
    response = table.scan()
    tasks = response.get('Items', [])

    tasks_to_remind = []

    for task in tasks:
        task_start_str = task['start_time']
        task_start_time = datetime.strptime(task_start_str, '%H:%M').time()

        # Combine with wedding date
        task_datetime = datetime.combine(WEDDING_DATE, task_start_time)
        task_datetime = TIMEZONE.localize(task_datetime)

        # Calculate reminder time (5 minutes before)
        reminder_time = task_datetime - timedelta(minutes=5)

        # Check if reminder should be sent in the next minute
        time_diff = (reminder_time - now).total_seconds()

        # Send if reminder is due within the next 60 seconds
        if 0 <= time_diff < 60:
            tasks_to_remind.append(task)
            logger.info(f"Task needs reminder: {task_start_str} - {task['task'][:50]}")

    return tasks_to_remind

def lambda_handler(event, context):
    """Lambda handler function"""
    logger.info("Lambda function started")

    try:
        tasks = get_tasks_to_remind()

        if not tasks:
            logger.info("No tasks need reminders at this time")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No reminders to send'})
            }

        # Send reminders
        for task in tasks:
            message = (
                f"⏰ *REMINDER* - Starting in 5 minutes!\n\n"
                f"{format_task_message(task)}"
            )

            send_telegram_message(message)

        logger.info(f"Sent {len(tasks)} reminders")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Sent {len(tasks)} reminders',
                'tasks': [t['task_id'] for t in tasks]
            })
        }

    except Exception as e:
        logger.error(f"Error in lambda handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# For local testing
if __name__ == '__main__':
    # Set environment variables for testing
    os.environ['TELEGRAM_BOT_TOKEN'] = 'your_token_here'
    os.environ['TELEGRAM_CHAT_ID'] = 'your_chat_id_here'

    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
