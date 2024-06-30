from aws_cdk import (
    Stack,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class GfpganSageMakerEndpointStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, ecr_image_uri: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM Role for SageMaker
        sagemaker_role = iam.Role(
            self, "GfpganSageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Create SageMaker Model
        model = sagemaker.CfnModel(
            self, "GfpganModel",
            execution_role_arn=sagemaker_role.role_arn,
            primary_container={
                "image": ecr_image_uri,
                "mode": "SingleModel",
                "environment": {
                    # Add any necessary environment variables here
                }
            },
            model_name="roop-model"
        )

        # Create SageMaker Endpoint Configuration
        endpoint_config = sagemaker.CfnEndpointConfig(
            self, "GfpganEndpointConfig",
            production_variants=[{
                "initialInstanceCount": 1,
                "instanceType": "ml.g4dn.xlarge",
                "modelName": model.model_name,
                "variantName": "AllTraffic"
            }],
            endpoint_config_name="gfpgan-sagemaker-endpoint-config"
        )

        # Create SageMaker Endpoint
        endpoint = sagemaker.CfnEndpoint(
            self, "GfpganEndpoint",
            endpoint_config_name=endpoint_config.endpoint_config_name,
            endpoint_name="gfpgan-sagemaker-endpoint"
        )

        # Add dependency to ensure correct deployment order
        endpoint.add_dependency(endpoint_config)
        endpoint_config.add_dependency(model)

        # Output the Endpoint Name
        CfnOutput(self, "GfpganSageMakerEndpointName", value=endpoint.endpoint_name)