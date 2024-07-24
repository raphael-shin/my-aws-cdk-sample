#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.streamlit_ecs_fargate_stack import StreamlitEcsFargateStack

app = cdk.App()

StreamlitEcsFargateStack(app, "StreamlitEcsFargateStack")

app.synth()
