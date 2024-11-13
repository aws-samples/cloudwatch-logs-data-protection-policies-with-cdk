import aws_cdk as cdk
from aws_cdk.assertions import Template
from aws_cdk.assertions import Match

from stacks.cloudwatch_policies import CloudwatchPolicesStack


def test_synthesizes_properly():
    app = cdk.App()

    # Create the ProcessorStack.
    cloudwatch_policies_stack = CloudwatchPolicesStack(
        app,
        "CloudwatchPolicesStack"
    )

    # Prepare the stack for assertions.
    template = Template.from_stack(cloudwatch_policies_stack)

    # Assert that we have the expected resources
    template.resource_count_is("AWS::Logs::LogGroup", 1)
    template.resource_count_is("AWS::Lambda::Function", 1)
    template.resource_count_is("AWS::IAM::Role", 1)
    template.resource_count_is("AWS::IAM::Policy", 3)
    template.resource_count_is("AWS::Lambda::Permission", 1)
    template.resource_count_is("AWS::Events::Rule", 1)
    template.resource_count_is("AWS::IAM::User", 2)

    template.has_resource_properties(
        "AWS::IAM::Role",
        Match.object_equals(
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {
                                    "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                            ]
                        ]
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::IAM::Role",
        Match.object_equals(
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {
                                    "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                            ]
                        ]
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        Match.object_equals(
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": "logs:Unmask",
                            "Effect": "Deny",
                            "Resource": "arn:aws:logs:*:*:*"
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "PolicyName": "UnmaskLogDenyPolicy",
                "Users": [
                    Match.any_value()
                ]
            }
        )
    )
        
    template.has_resource_properties(
        "AWS::IAM::Policy",
        Match.object_equals(
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": "logs:Unmask",
                            "Effect": "Allow",
                            "Resource":"arn:aws:logs:*:*:*"
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "PolicyName": "UnmaskLogAllowPolicy",
                "Users": [
                    Match.any_value()
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::Events::Rule",
        Match.object_equals(
            {
                "ScheduleExpression": "rate(1 minute)",
                "State": "ENABLED",
                "Targets": [
                    {
                        "Arn": {
                            "Fn::GetAtt": [
                                Match.any_value(),
                                "Arn"
                            ]
                        },
                        "Id": "Target0"
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::IAM::User",
        Match.object_equals(
            {
                "LoginProfile": {
                "Password": Match.any_value()
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [    
                                "arn:",
                                {
                                    "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/CloudWatchLogsReadOnlyAccess"
                            ]
                        ]
                    }
                ],
                "UserName": "DemoLogAdmin"
            }
        )
    )

    template.has_resource_properties(
        "AWS::IAM::User",
        Match.object_equals(
            {
                "LoginProfile": {
                "Password": Match.any_value()
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [    
                                "arn:",
                                {
                                    "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/CloudWatchLogsReadOnlyAccess"
                            ]
                        ]
                    }
                ],
                "UserName": "DemoLogViewer"
            }
        )
    )
