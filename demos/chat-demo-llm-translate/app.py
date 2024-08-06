import aws_cdk as cdk

from stacks.streamlit_ecs_fargate_stack import StreamlitEcsFargateStack
from stacks.dynamodb_stack import DynamoDBStack

app = cdk.App()

# DynamoDB 스택 생성
dynamodb_stack = DynamoDBStack(app, "DynamoDBStack")

# Streamlit ECS Fargate 스택 생성 및 DynamoDB 테이블 전달
streamlit_stack = StreamlitEcsFargateStack(app, "StreamlitEcsFargateStack",
    dynamodb_table=dynamodb_stack.table
)

# DynamoDB 스택에 대한 의존성 추가
streamlit_stack.add_dependency(dynamodb_stack)

app.synth()