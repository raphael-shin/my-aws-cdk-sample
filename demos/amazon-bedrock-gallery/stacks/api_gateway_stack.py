from aws_cdk import (
    Stack,
    CfnOutput,
    aws_apigateway as apigw,
    aws_lambda as lambda_
)
from constructs import Construct
import os

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.s3_bucket_name = self.node.try_get_context("s3_bucket_name")
        self.s3_face_images_path = self.node.try_get_context("s3_face_images_path")
        self.s3_result_images_path = self.node.try_get_context("s3_result_images_path")

        self.api = self.create_api_gateway()
        self.upload_lambda = self.create_lambda_function("UploadImageFunction", "upload", self.s3_face_images_path)
        self.get_image_lambda = self.create_lambda_function("GetImageFunction", "get_image", self.s3_result_images_path)

        self.create_api_resources()
        self.create_output()

    def create_api_gateway(self):
        return apigw.RestApi(self, "AmazonBedrockGalleryImageApi",
            rest_api_name="Amazon Bedrock Gallery Image API",
            description="This service processes images.")

    def create_lambda_function(self, id, handler, object_path):
        return lambda_.Function(self, id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler=f"{handler}.handler",
            code=lambda_.Code.from_asset(os.path.join("lambda", "apis", handler)),
            environment={
                "BUCKET_NAME": self.s3_bucket_name,
                "OBJECT_PATH": object_path
            })

    def create_api_resources(self):
        images_resource = self.api.root.add_resource("apis").add_resource("images")
        
        self.create_upload_resource(images_resource)
        self.create_get_image_resource(images_resource)

    def create_upload_resource(self, parent_resource):
        upload_resource = parent_resource.add_resource("upload")
        upload_integration = apigw.LambdaIntegration(self.upload_lambda)
        upload_resource.add_method("POST", upload_integration)

    def create_get_image_resource(self, parent_resource):
        image_resource = parent_resource.add_resource("{uuid}")
        get_image_integration = apigw.LambdaIntegration(self.get_image_lambda)
        image_resource.add_method("GET", get_image_integration)

    def create_output(self):
        CfnOutput(self, "ApiGatewayUrl", value=self.api.url, description="The URL of the API Gateway")