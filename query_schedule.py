#!/usr/bin/env python3
"""
Simple script to query the wedding schedule without running the full bot
"""
import boto3
from datetime import datetime, timedelta
import pytz

TABLE_NAME = 'WeddingSchedule'
TIMEZONE = pytz.timezone('Asia/Singapore')

def format_task_message(task):
    """Format a task into a readable message"""
    people_str = ', '.join(task['people'])
    role_emoji = {
        'bride': '❤️',
        'groom': '💙',
        'bridesmaid': '👭',
        'groomsmen': '👬',
        'test': '🧪'
    }

    emoji = role_emoji.get(task['role'], '📋')
    return (
        f"{emoji} {task['role'].title()} [{task['start_time']}-{task['end_time']}]\n"
        f"   👥 {people_str}\n"
        f"   📝 {task['task'][:80]}...\n"
    )

def get_tasks_in_timerange(start_time, end_time):
    """Get all tasks within a time range"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(TABLE_NAME)

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

def query_next_15_minutes():
    """Query tasks in the next 15 minutes"""
    now = datetime.now(TIMEZONE)
    start_time = now.time()
    end_time = (now + timedelta(minutes=15)).time()

    print(f"Current time (SGT): {now.strftime('%H:%M:%S')}")
    print(f"Querying tasks from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
    print("=" * 80)

    tasks = get_tasks_in_timerange(start_time, end_time)

    if not tasks:
        print("\n📭 No tasks scheduled in the next 15 minutes!")
    else:
        print(f"\n📅 Found {len(tasks)} task(s) in the next 15 minutes:\n")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {format_task_message(task)}")

def query_next_hour():
    """Query tasks in the next hour"""
    now = datetime.now(TIMEZONE)
    start_time = now.time()
    end_time = (now + timedelta(minutes=60)).time()

    print(f"Current time (SGT): {now.strftime('%H:%M:%S')}")
    print(f"Querying tasks from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
    print("=" * 80)

    tasks = get_tasks_in_timerange(start_time, end_time)

    if not tasks:
        print("\n📭 No tasks scheduled in the next hour!")
    else:
        print(f"\n📅 Found {len(tasks)} task(s) in the next hour:\n")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {format_task_message(task)}")

def query_all_today():
    """Query all tasks today"""
    print("Current time (SGT): " + datetime.now(TIMEZONE).strftime('%H:%M:%S'))
    print("Querying all tasks for today")
    print("=" * 80)

    start_time = datetime.min.time()
    end_time = datetime.max.time()

    tasks = get_tasks_in_timerange(start_time, end_time)

    if not tasks:
        print("\n📭 No tasks scheduled today!")
    else:
        print(f"\n📅 Found {len(tasks)} task(s) today:\n")

        # Group by hour
        by_hour = {}
        for task in tasks:
            hour = task['start_time'][:2]
            if hour not in by_hour:
                by_hour[hour] = []
            by_hour[hour].append(task)

        for hour in sorted(by_hour.keys()):
            print(f"\n⏰ {hour}:00 hour ({len(by_hour[hour])} tasks)")
            for task in by_hour[hour]:
                print(f"  • {task['start_time']}-{task['end_time']}: {task['task'][:60]}...")

def main():
    """Main function"""
    import sys

    print("\n" + "=" * 80)
    print("WEDDING SCHEDULE QUERY TOOL")
    print("=" * 80 + "\n")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_schedule.py next15   # Next 15 minutes")
        print("  python query_schedule.py next60   # Next hour")
        print("  python query_schedule.py today    # All tasks today")
        print()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in ['next15', '15']:
        query_next_15_minutes()
    elif command in ['next60', '60', 'hour']:
        query_next_hour()
    elif command in ['today', 'all']:
        query_all_today()
    else:
        print(f"Unknown command: {command}")
        print("Use: next15, next60, or today")
        sys.exit(1)

if __name__ == '__main__':
    main()
