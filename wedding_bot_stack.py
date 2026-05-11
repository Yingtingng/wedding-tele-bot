"""
CDK Stack for Wedding Reminder Bot
"""
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_logs as logs,
    aws_apigateway as apigw,
)
import aws_cdk as cdk


class WeddingBotStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        telegram_token: str,
        chat_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        table = dynamodb.Table(
            self,
            "WeddingScheduleTable",
            table_name="WeddingSchedule",
            partition_key=dynamodb.Attribute(
                name="task_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand pricing
            removal_policy=RemovalPolicy.DESTROY,  # Be careful with this in production!
            point_in_time_recovery=False,  # Not needed for single-day event
        )

        # Global Secondary Index for querying by time
        table.add_global_secondary_index(
            index_name="TimeIndex",
            partition_key=dynamodb.Attribute(
                name="start_time",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # Global Secondary Index for querying by role and time
        table.add_global_secondary_index(
            index_name="RoleIndex",
            partition_key=dynamodb.Attribute(
                name="role",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="start_time",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # Lambda Layer with dependencies
        lambda_layer = lambda_.LayerVersion(
            self,
            "WeddingBotDependencies",
            code=lambda_.Code.from_asset("lambda_layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Dependencies for Wedding Bot: requests, pytz",
        )

        # Lambda Function for Reminders
        reminder_function = lambda_.Function(
            self,
            "ReminderFunction",
            function_name="wedding-reminder-bot",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_reminder.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "TELEGRAM_BOT_TOKEN": telegram_token,
                "TELEGRAM_CHAT_ID": chat_id,
                "DYNAMODB_TABLE": table.table_name,
            },
            layers=[lambda_layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Grant Lambda permission to read from DynamoDB
        table.grant_read_data(reminder_function)

        # EventBridge Rule - trigger every minute
        rule = events.Rule(
            self,
            "ReminderScheduleRule",
            schedule=events.Schedule.rate(Duration.minutes(1)),
            description="Trigger wedding reminders every minute",
        )

        rule.add_target(targets.LambdaFunction(reminder_function))

        # Lambda Function for Bot Webhook
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
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        table.grant_read_data(bot_webhook_function)

        # API Gateway for Telegram Webhook
        api = apigw.RestApi(
            self,
            "BotWebhookApi",
            rest_api_name="wedding-bot-webhook",
            description="Webhook endpoint for Telegram bot",
            deploy_options=apigw.StageOptions(
                throttling_rate_limit=10,
                throttling_burst_limit=20
            )
        )

        # Webhook endpoint
        webhook = api.root.add_resource("webhook")
        webhook.add_method(
            "POST",
            apigw.LambdaIntegration(
                bot_webhook_function,
                proxy=False,
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": ""
                        }
                    )
                ]
            ),
            method_responses=[
                apigw.MethodResponse(status_code="200")
            ]
        )

        # Outputs
        cdk.CfnOutput(
            self,
            "DynamoDBTableName",
            value=table.table_name,
            description="DynamoDB table name for wedding schedule"
        )

        cdk.CfnOutput(
            self,
            "ReminderFunctionArn",
            value=reminder_function.function_arn,
            description="Lambda function ARN for reminder bot"
        )

        cdk.CfnOutput(
            self,
            "BotWebhookFunctionArn",
            value=bot_webhook_function.function_arn,
            description="Lambda function ARN for bot webhook"
        )

        cdk.CfnOutput(
            self,
            "EventRuleName",
            value=rule.rule_name,
            description="EventBridge rule name"
        )

        cdk.CfnOutput(
            self,
            "WebhookUrl",
            value=api.url + "webhook",
            description="Telegram webhook URL - use this to register webhook with Telegram",
            export_name="WeddingBotWebhookUrl"
        )
