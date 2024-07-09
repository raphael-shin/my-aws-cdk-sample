import json
import boto3
import os
import time
import urllib.parse

sagemaker_runtime = boto3.client('sagemaker-runtime')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    s3_event = event['Records'][0]['s3']
    bucket = s3_event['bucket']['name']
    source_key = urllib.parse.unquote_plus(s3_event['object']['key'])
    uuid = os.path.basename(source_key).split('.')[0]
    output_key = f"{os.environ['OUTPUT_PATH']}{uuid}.png"
    
    # Prepare the input for the SageMaker endpoint
    input_data = {
        'uuid': uuid,
        'bucket': bucket,
        'source': source_key,
        'output': output_key
    }
    
    try:
        # Invoke the SageMaker endpoint
        sagemaker_runtime.invoke_endpoint(
            EndpointName=os.environ['SAGEMAKER_ENDPOINT_NAME'],
            ContentType='application/json',
            Body=json.dumps(input_data)
        )
        
        # Check if the output file exists in S3
        start_time = time.time()
        max_wait_time = 15  # Maximum wait time in seconds
        check_interval = 0.5  # Time between checks in seconds
        
        while time.time() - start_time < max_wait_time:
            try:
                s3.head_object(Bucket=bucket, Key=output_key)
                s3_url = f's3://{bucket}/{output_key}'
                print(f"Processing completed successfully. Output: {s3_url}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Processing completed successfully',
                        'output_url': s3_url
                    })
                }
            except s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] != '404':
                    raise
            time.sleep(check_interval)
        
        raise Exception(f"Output file not found in S3 after {max_wait_time} seconds: {output_key}")
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }