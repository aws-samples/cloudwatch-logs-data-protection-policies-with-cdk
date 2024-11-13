#!/usr/bin/env python3

import aws_cdk

from stacks.cloudwatch_policies import CloudwatchPolicesStack

app = aws_cdk.App()

CloudwatchPolicesStack(
    app,
    "CloudwatchPolicesStack"
)

app.synth()
