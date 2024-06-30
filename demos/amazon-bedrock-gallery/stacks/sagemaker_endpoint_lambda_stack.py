from aws_cdk import CfnOutput, Stack, Duration
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
from constructs import Construct

class SageMakerEndpointLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, roop_endpoint_name: str, gfpgan_endpoint_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for Lambda functions
        lambda_role = iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Create Roop Lambda function
        roop_lambda = lambda_.Function(self, "RoopLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/roop"),
            timeout=Duration.seconds(300),
            memory_size=1024,
            environment={
                "SAGEMAKER_ENDPOINT_NAME": roop_endpoint_name
            },
            role=lambda_role
        )

        # Create GFPGAN Lambda function
        gfpgan_lambda = lambda_.Function(self, "GfpganLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/gfpgan"),
            timeout=Duration.seconds(300),
            memory_size=1024,
            environment={
                "SAGEMAKER_ENDPOINT_NAME": gfpgan_endpoint_name
            },
            role=lambda_role
        )

        # Output the Lambda function names and ARNs
        self.roop_lambda_name = roop_lambda.function_name
        self.roop_lambda_arn = roop_lambda.function_arn
        self.gfpgan_lambda_name = gfpgan_lambda.function_name
        self.gfpgan_lambda_arn = gfpgan_lambda.function_arn

        # Outputs for Roop Lambda
        CfnOutput(self, "RoopLambdaName", value=roop_lambda.function_name, description="The name of the Roop Lambda function")
        
        CfnOutput(self, "RoopLambdaArn", value=roop_lambda.function_arn, description="The ARN of the Roop Lambda function")

        # Outputs for GFPGAN Lambda
        CfnOutput(self, "GfpganLambdaName", value=gfpgan_lambda.function_name, description="The name of the GFPGAN Lambda function")
        
        CfnOutput(self, "GfpganLambdaArn", value=gfpgan_lambda.function_arn, description="The ARN of the GFPGAN Lambda function")