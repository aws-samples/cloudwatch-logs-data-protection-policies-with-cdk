import os

from aws_cdk import CfnOutput, Duration, SecretValue, Stack, aws_lambda
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import RemovalPolicy
from constructs import Construct

from stacks.utils import StackUtils


class CloudwatchPolicesStack(Stack):

    PRIVILEGED_USER_NAME = "DemoLogAdmin"
    STANDARD_USER_NAME = "DemoLogViewer"


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = StackUtils.read_cdk_context_json()['app_properties']

        ##########################################################
        # <START> LogGroups and Data Protection Policies
        ##########################################################

        data_protection_policy = logs.DataProtectionPolicy(
            name="LoggerDataProtectionPolicy",
            description="Demo data protection policy for Logger Lambda",
            identifiers=[
                logs.DataIdentifier.EMAILADDRESS,
                logs.DataIdentifier.IPADDRESS,
                logs.CustomDataIdentifier('EmployeeId', 'EmployeeId-\d{9}')
            ]
        )

        lambda_log_group = logs.LogGroup(
            self,
            "LoggerLambdaLogGroup",
            log_group_name="LoggerLambdaDemoLogGroup",
            data_protection_policy=data_protection_policy,
            removal_policy=RemovalPolicy.DESTROY
        )

        ##########################################################
        # </END> LogGroups and Data Protection Policies
        ##########################################################

        ##########################################################
        # <START> Lambda resources
        ##########################################################

        # IAM Role for Lambda
        logger_lambda_role = iam.Role(
            scope=self,
            id="LoggerLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
  
        logger_lambda_role.add_to_policy(
            iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:logs:*:*:*"],
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:ListLogDeliveries"
                    ]
                )
        )

        logger_lambda = aws_lambda.Function(
            scope=self,
            id="LoggerLambda",
            code=aws_lambda.Code.from_asset(f"{os.path.dirname(__file__)}/resources/logger"),
            handler="logger.lambda_handler",
            role=logger_lambda_role,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(15),
            log_group=lambda_log_group
        )

        # Scheduled event to trigger lambda function every minute
        event_rule = events.Rule(
            self,
            'LambdaScheduleRule',
            schedule=events.Schedule.rate(duration=Duration.minutes(1))
        )

        event_rule.add_target(targets.LambdaFunction(logger_lambda))

        ##########################################################
        # </END> Lambda resources
        ##########################################################


        ##########################################################
        # <START> User creation
        ##########################################################

        privileged_user = iam.User(
            self,
            'DemoLogAdminUser',
            user_name=self.PRIVILEGED_USER_NAME,
            password=SecretValue.unsafe_plain_text(config['privileged_user_password']),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsReadOnlyAccess')
            ]
        )

        unmask_allow_policy = iam.Policy(
            self,
            'UnmaskLogAllowPolicy',
            policy_name='UnmaskLogAllowPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=['logs:Unmask'],
                    resources=['arn:aws:logs:*:*:*']
                )
            ]
        )

        unmask_allow_policy.attach_to_user(privileged_user)

        standard_user = iam.User(
            self,
            'DemoLogViewerUser',
            user_name=self.STANDARD_USER_NAME,
            password=SecretValue.unsafe_plain_text(config['standard_user_password']),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsReadOnlyAccess')
            ]
        )

        unmask_deny_policy = iam.Policy(
            self,
            'UnmaskLogDenyPolicy',
            policy_name='UnmaskLogDenyPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=['logs:Unmask'],
                    resources=['arn:aws:logs:*:*:*']
                )
            ]
        )

        unmask_deny_policy.attach_to_user(standard_user)

        ##########################################################
        # </END> User creation
        ##########################################################


        ##########################################################
        # <START> Stack exports
        ##########################################################

        CfnOutput(
            self, 
            id="LambdaLoggerLogGroupName", 
            value=lambda_log_group.log_group_name, 
            export_name="LambdaLoggerLogGroupName"
        )

        CfnOutput(
            self, 
            id="LambdaLoggerLogGroupArn", 
            value=lambda_log_group.log_group_arn, 
            export_name="LambdaLoggerLogGroupArn"
        )
        
        CfnOutput(
            self, 
            id="LoggerLambdaFunctionArn", 
            value=logger_lambda.function_arn, 
            export_name="LoggerLambdaFunctionArn"
        )

        CfnOutput(
            self, 
            id="LoggerLambdaFunctionName", 
            value=logger_lambda.function_name, 
            export_name="LoggerLambdaFunctionName"
        )

        CfnOutput(
            self, 
            id="PrivilegedUserName", 
            value=privileged_user.user_name, 
            export_name="PrivilegedUserName"
        )

        CfnOutput(
            self, 
            id="StandardUserName", 
            value=standard_user.user_name, 
            export_name="StandardUserName"
        )
       
        ##########################################################
        # </END> Stack exports
        ##########################################################
