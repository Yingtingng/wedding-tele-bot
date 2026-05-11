#!/usr/bin/env python3
"""
Insert 3 additional tasks for Karina, Rana, and Robert
"""
import boto3

TABLE_NAME = 'WeddingSchedule'
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table(TABLE_NAME)

# Define the 3 new tasks
NEW_TASKS = [
    {
        'task_id': '09:30_bridesmaid_karina_1',
        'start_time': '09:30',
        'end_time': '09:40',
        'task': '👭 Take floral bracelet from fridge',
        'role': 'bridesmaid',
        'people': ['Karina'],
        'wedding_date': '2026-05-09',
        'timezone': 'Asia/Singapore'
    },
    {
        'task_id': '10:30_bridesmaid_karina_2',
        'start_time': '10:30',
        'end_time': '10:40',
        'task': '👭 Pass floral bracelet to Maribelle, Sam and Sophia at the church',
        'role': 'bridesmaid',
        'people': ['Karina'],
        'wedding_date': '2026-05-09',
        'timezone': 'Asia/Singapore'
    },
    {
        'task_id': '18:40_groomsmen_hedges',
        'start_time': '18:40',
        'end_time': '18:50',
        'task': '👬 Help to bring down 2 floral hedges from tea ceremony room to the aisle',
        'role': 'groomsmen',
        'people': ['Rana', 'Robert'],
        'wedding_date': '2026-05-09',
        'timezone': 'Asia/Singapore'
    },
]

def main():
    print("=" * 80)
    print("INSERTING 3 ADDITIONAL TASKS")
    print("=" * 80)
    print()

    for i, task in enumerate(NEW_TASKS, 1):
        print(f"Task {i}:")
        print(f"  Time: {task['start_time']} - {task['end_time']}")
        print(f"  People: {', '.join(task['people'])}")
        print(f"  Task: {task['task']}")
        print()

    print("=" * 80)
    response = input("Add these 3 tasks to DynamoDB? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled. No tasks added.")
        return

    print()
    print("Adding tasks to DynamoDB...")
    print("-" * 80)

    with table.batch_writer() as batch:
        for task in NEW_TASKS:
            batch.put_item(Item=task)
            print(f"✅ Added: [{task['start_time']}-{task['end_time']}] {task['task']}")

    print()
    print("=" * 80)
    print(f"✅ SUCCESS! Added {len(NEW_TASKS)} tasks to the wedding schedule")
    print("=" * 80)
    print()
    print("Reminders will be sent:")
    print("  - 09:25 AM → Karina: Take floral bracelet from fridge")
    print("  - 10:25 AM → Karina: Pass floral bracelet to church guests")
    print("  - 06:35 PM → Rana, Robert: Bring down hedges")
    print()

if __name__ == '__main__':
    main()
