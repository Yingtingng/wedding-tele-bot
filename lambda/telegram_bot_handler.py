#!/usr/bin/env python3
"""
Lambda handler for Telegram bot webhook (alternative to polling)
For webhook-based deployment with API Gateway
"""
import os
import json
import logging
from datetime import datetime, timedelta
import boto3
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
TABLE_NAME = os.getenv('DYNAMODB_TABLE', 'WeddingSchedule')
TIMEZONE = pytz.timezone('Asia/Singapore')
WEDDING_DATE = datetime(2026, 5, 9, tzinfo=TIMEZONE).date()

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
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

def handle_query(query_type):
    """Handle different query types"""
    now = datetime.now(TIMEZONE)

    if query_type == 'next_15':
        start_time = now.time()
        end_time = (now + timedelta(minutes=15)).time()
        title = "Next 15 minutes"
    elif query_type == 'next_60':
        start_time = now.time()
        end_time = (now + timedelta(minutes=60)).time()
        title = "Next hour"
    elif query_type == 'all_today':
        start_time = datetime.min.time()
        end_time = datetime.max.time()
        title = "All tasks today"
    else:
        return "Unknown query type"

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

    return message

def lambda_handler(event, context):
    """Lambda handler for webhook-based bot"""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Parse incoming webhook from Telegram
        # API Gateway may wrap in 'body' or pass through directly
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event

        # Get chat_id from the message
        chat_id = None
        text = ""

        # Handle different update types
        if 'message' in body:
            message = body['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')

            logger.info(f"Received message: {text} from chat {chat_id}")

            # Only respond to specific commands, ignore everything else
            if text == '/start':
                response_text = (
                    '👰🤵 Wedding Schedule Bot 👰🤵\n\n'
                    'Use these commands:\n'
                    '/next15 - Next 15 minutes\n'
                    '/next60 - Next hour\n'
                )
            elif text == '/next15':
                response_text = handle_query('next_15')
            elif text == '/next60':
                response_text = handle_query('next_60')
            else:
                # Not a recognized command - ignore silently
                logger.info(f"Ignoring non-command message: {text}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({'ok': True})
                }

        elif 'callback_query' in body:
            callback = body['callback_query']
            chat_id = callback['message']['chat']['id']
            data = callback.get('data', '')
            response_text = handle_query(data)

        else:
            logger.warning("Unknown update type")
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }

        # Send response back via Telegram API
        import requests
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            'chat_id': chat_id,
            'text': response_text
        }

        # Try with Markdown first, fallback to plain text
        try:
            payload['parse_mode'] = 'Markdown'
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
        except:
            payload.pop('parse_mode', None)
            resp = requests.post(url, json=payload)

        logger.info(f"Response sent to chat {chat_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }

    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        return {
            'statusCode': 200,  # Always return 200 to Telegram
            'body': json.dumps({'ok': True})
        }
