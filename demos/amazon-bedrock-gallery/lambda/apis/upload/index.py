import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    # TODO: BUCKET_NAME에 해당하는 버킷에 업로그를 할 수 있는 presigned URL을 생성하고 반환 (유효시간은 5분)
    return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'presignedUrl': ''})
        }