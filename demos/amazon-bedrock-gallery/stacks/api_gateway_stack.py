from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as lambda_
from constructs import Construct
import os

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the bucket name from context
        s3_face_image_bucket_name = self.node.try_get_context("s3_face_image_bucket_name")
        s3_result_image_bucket_name = self.node.try_get_context("s3_result_image_bucket_name")

        # Create API Gateway
        api = apigw.RestApi(self, "AmazonBedrockGalleryImageApi",
            rest_api_name="Amazon Bedrock Gallery Image API",
            description="This service processes images.")

        # Create Lambda function for image upload
        upload_lambda = lambda_.Function(self, "UploadImageFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="upload.handler",
            code=lambda_.Code.from_asset(os.path.join("lambda", "apis/upload")),
            environment={
                "BUCKET_NAME": s3_face_image_bucket_name
            })

        # Create Lambda function for image retrieval
        get_image_lambda = lambda_.Function(self, "GetImageFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="get_image.handler",
            code=lambda_.Code.from_asset(os.path.join("lambda", "apis/get_image")),
            environment={
                "BUCKET_NAME": s3_result_image_bucket_name
            })

        # Create API Gateway resources and methods
        images_resource = api.root.add_resource("apis").add_resource("images")
        
        upload_resource = images_resource.add_resource("upload")
        upload_integration = apigw.LambdaIntegration(upload_lambda)
        upload_resource.add_method("POST", upload_integration)

        image_resource = images_resource.add_resource("{uuid}")
        get_image_integration = apigw.LambdaIntegration(get_image_lambda)
        image_resource.add_method("GET", get_image_integration)

        # Output the API Gateway URL
        CfnOutput(self, "ApiGatewayUrl", value=api.url, description="The URL of the API Gateway")