#!/usr/bin/env python3
"""
DynamoDB table schema and data upload script
"""
import boto3
import json
from datetime import datetime
from decimal import Decimal

TABLE_NAME = 'WeddingSchedule'

def create_table():
    """Create DynamoDB table with proper schema"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')

    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {'AttributeName': 'task_id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'task_id', 'AttributeType': 'S'},
            {'AttributeName': 'start_time', 'AttributeType': 'S'},
            {'AttributeName': 'role', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'TimeIndex',
                'KeySchema': [
                    {'AttributeName': 'start_time', 'KeyType': 'HASH'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'RoleIndex',
                'KeySchema': [
                    {'AttributeName': 'role', 'KeyType': 'HASH'},
                    {'AttributeName': 'start_time', 'KeyType': 'RANGE'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    print(f"Creating table {TABLE_NAME}...")
    table.wait_until_exists()
    print(f"Table {TABLE_NAME} created successfully!")

    return table

def upload_tasks(schedule_file='schedule.json'):
    """Upload tasks from JSON to DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(TABLE_NAME)

    with open(schedule_file, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    print(f"Uploading {len(tasks)} tasks to DynamoDB...")

    with table.batch_writer() as batch:
        for idx, task in enumerate(tasks):
            # Create unique task_id
            task_id = f"{task['start_time']}_{task['role']}_{idx}"

            item = {
                'task_id': task_id,
                'start_time': task['start_time'],
                'end_time': task['end_time'],
                'task': task['task'],
                'role': task['role'],
                'people': task['people'],
                'wedding_date': '2026-05-09',
                'timezone': 'Asia/Singapore'
            }

            batch.put_item(Item=item)

            if (idx + 1) % 10 == 0:
                print(f"Uploaded {idx + 1}/{len(tasks)} tasks...")

    print(f"Successfully uploaded {len(tasks)} tasks!")

def list_tasks():
    """List all tasks in the table"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    table = dynamodb.Table(TABLE_NAME)

    response = table.scan(Limit=10)
    items = response.get('Items', [])

    print(f"\nFirst 10 tasks in DynamoDB:")
    print("=" * 80)
    for item in items:
        print(f"[{item['start_time']}-{item['end_time']}] {item['role']}")
        print(f"  Task: {item['task'][:60]}")
        print(f"  People: {', '.join(item['people'])}\n")

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python dynamodb_schema.py [create|upload|list]")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'create':
        create_table()
    elif command == 'upload':
        upload_tasks()
    elif command == 'list':
        list_tasks()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, upload, list")
