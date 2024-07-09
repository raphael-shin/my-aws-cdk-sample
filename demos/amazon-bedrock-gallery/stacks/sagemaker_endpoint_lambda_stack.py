from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_s3_deployment as s3deploy,
    aws_lambda_event_sources as lambda_events,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    Fn,
    CfnOutput, Stack, Duration
)
from constructs import Construct

class SageMakerEndpointLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, roop_endpoint_name: str, gfpgan_endpoint_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "ImageBucket",
            bucket_name=Fn.join('-', ['bedrock-y', Fn.ref('AWS::AccountId')]),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Klayers-p38-Pillow Layer 참조
        pillow_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "PillowLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-Pillow:10"
        )

        # Klayers-p38-numpy Layer 참조
        numpy_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "NumpyLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-numpy:13"
        )

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

        # Face Detection Lambda 함수 생성
        face_detection_lambda = lambda_.Function(self, "FaceDetectionLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset("lambda/face_detection"),
            timeout=Duration.seconds(300),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
            layers=[pillow_layer, numpy_layer]
        )

        # Lambda 함수에 필요한 권한 부여
        bucket.grant_read_write(face_detection_lambda)
        face_detection_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["rekognition:DetectFaces"],
            resources=["*"]
        ))

        # face detection S3 이벤트 트리거 설정
        face_detection_lambda.add_event_source(lambda_events.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="gallery/images/faces/")]
        ))

        # roop S3 이벤트 트리거 설정
        roop_lambda.add_event_source(lambda_events.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="gallery/images/masked-faces/")]
        ))

        # gfpgan S3 이벤트 트리거 설정
        gfpgan_lambda.add_event_source(lambda_events.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="gallery/images/roop/")]
        ))
        
        # Output the Lambda function names and ARNs
        self.roop_lambda_name = roop_lambda.function_name
        self.roop_lambda_arn = roop_lambda.function_arn
        self.gfpgan_lambda_name = gfpgan_lambda.function_name
        self.gfpgan_lambda_arn = gfpgan_lambda.function_arn
        self.face_detection_lambda_name = face_detection_lambda.function_name
        self.face_detection_lambda_arn = face_detection_lambda.function_arn

        # Outputs for Roop Lambda
        CfnOutput(self, "RoopLambdaName", value=roop_lambda.function_name, description="The name of the Roop Lambda function")
        
        CfnOutput(self, "RoopLambdaArn", value=roop_lambda.function_arn, description="The ARN of the Roop Lambda function")

        # Outputs for GFPGAN Lambda
        CfnOutput(self, "GfpganLambdaName", value=gfpgan_lambda.function_name, description="The name of the GFPGAN Lambda function")
        
        CfnOutput(self, "GfpganLambdaArn", value=gfpgan_lambda.function_arn, description="The ARN of the GFPGAN Lambda function")

        # Outputs for face detection Lambda
        CfnOutput(self, "FaceDetectionLambdaName", value=face_detection_lambda.function_name, description="The name of the FaceDetection Lambda function")
        
        CfnOutput(self, "FaceDetectionLambdaArn", value=face_detection_lambda.function_arn, description="The ARN of the FaceDetection Lambda function")