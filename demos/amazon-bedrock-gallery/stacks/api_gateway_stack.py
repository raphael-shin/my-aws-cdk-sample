from aws_cdk import (
    Stack,
    CfnOutput,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_ssm as ssm
)
from constructs import Construct
import os

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_base_bucket_name = self.node.try_get_context("s3_base_bucket_name")
        self.s3_bucket_name = f"{s3_base_bucket_name}-{self.account}"
        self.s3_face_images_path = self.node.try_get_context("s3_face_images_path")
        self.s3_result_images_path = self.node.try_get_context("s3_result_images_path")

        self.api = self.create_api_gateway()
        self.upload_lambda = self.create_lambda_function("UploadImageFunction", "upload", self.s3_face_images_path)
        self.get_image_lambda = self.create_lambda_function("GetImageFunction", "get_image", self.s3_result_images_path)

        self.create_api_resources()
        self.store_api_endpoints_in_ssm()
        self.create_output()

    def create_api_gateway(self):
        return apigw.RestApi(self, "AmazonBedrockGalleryImageApi",
            rest_api_name="Amazon Bedrock Gallery Image API",
            description="This service processes images.")

    def create_lambda_function(self, id, handler, object_path):
        return lambda_.Function(self, id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler=f"index.handler",
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

    def store_api_endpoints_in_ssm(self):
        upload_endpoint = f"{self.api.url}apis/images/upload"
        get_image_endpoint = f"{self.api.url}apis/images/"

        ssm.StringParameter(self, "UploadApiEndpointParameter",
            parameter_name="/genai-gallery/upload-image-api-endpoint",
            string_value=upload_endpoint,
            description="Upload Image API Endpoint URL"
        )

        ssm.StringParameter(self, "GetImageApiEndpointParameter",
            parameter_name="/genai-gallery/get-image-api-endpoint",
            string_value=get_image_endpoint,
            description="Get Image API Endpoint URL"
        )
        
    def create_output(self):
        CfnOutput(self, "ApiGatewayUrl", value=self.api.url, description="The URL of the API Gateway")