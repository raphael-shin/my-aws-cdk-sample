import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    # TODO: BUCKET_NAME에 해당하는 버킷에서 uuid(objectkey)에 해당하는 이미지를 가져올 수 있는 presigned URL을 생성하고 반환 (유효시간은 1시간)
    return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'presignedUrl': ''})
        }