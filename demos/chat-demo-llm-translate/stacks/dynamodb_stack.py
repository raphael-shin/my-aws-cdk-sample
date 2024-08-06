from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DynamoDBStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB 테이블 생성 (테이블 이름 고정)
        self.table = dynamodb.Table(
            self, "ChatMessages",
            table_name="ChatMessages",  # 고정된 테이블 이름 사용
            partition_key=dynamodb.Attribute(name="room_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # 테이블 이름을 CloudFormation 출력으로 추가
        CfnOutput(self, "ChatMessagesTableName",
            value=self.table.table_name,
            description="The name of the ChatMessages table",
            export_name="ChatMessagesTableName"
        )