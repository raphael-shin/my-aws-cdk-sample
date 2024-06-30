import json
import boto3
import os
import uuid

sagemaker_runtime = boto3.client('sagemaker-runtime')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Generate a unique ID for this invocation
    invocation_id = str(uuid.uuid4())
    
    # Extract information from the event
    bucket = event['bucket']
    source_key = event['source']
    output_key = event['output']
    
    # Prepare the input for the SageMaker endpoint
    input_data = {
        'uuid': invocation_id,
        'bucket': bucket,
        'source': source_key,
        'output': output_key
    }
    
    # Invoke the SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=os.environ['SAGEMAKER_ENDPOINT_NAME'],
        ContentType='application/json',
        Body=json.dumps(input_data)
    )
    
    # Parse the response
    result = json.loads(response['Body'].read().decode())
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }