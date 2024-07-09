import boto3
import copy
from PIL import Image
from io import BytesIO
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # S3에서 이미지 파일을 로드
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image = Image.open(response['Body'])
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Rekognition으로 가장 큰 얼굴 영역 추출
    cropped_image, width, height, f_left, f_top, f_width, f_height, _ = show_faces(image, padding_ratio=0.5)
    
    if cropped_image is not None:
        # 추출한 얼굴 영역을 새로운 이미지로 저장
        cropped_image = cropped_image.crop((f_left, f_top, f_left + f_width, f_top + f_height))
        
        # 새로운 S3 버킷과 키 지정
        account_id = context.invoked_function_arn.split(":")[4]
        new_bucket_name = f'bedrock-y-{account_id}'
        new_key = 'gallery/images/masked-faces/' + key.split('/')[-1]
        
        
        # 추출한 이미지를 S3에 저장
        buffered = BytesIO()
        cropped_image.save(buffered, format="png")
        image_bytes = buffered.getvalue()
        s3.put_object(Bucket=new_bucket_name, Key=new_key, Body=image_bytes)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Cropped face image saved successfully!')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('No faces detected in the image.')
        }

def show_faces(image, target_region='us-east-1', padding_ratio=0.1):
    client = boto3.client('rekognition', region_name=target_region)
    
    imgWidth, imgHeight = image.size
    ori_image = copy.deepcopy(image)
    
    buffer = BytesIO()
    image.save(buffer, format='jpeg')
    val = buffer.getvalue()
    
    response = client.detect_faces(Image={'Bytes': val}, Attributes=['ALL'])
    
    largest_area = 0
    largest_face_box = None
    
    for faceDetail in response['FaceDetails']:
        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
        
        current_area = width * height
        
        if current_area > largest_area:
            largest_area = current_area
            largest_face_box = (left, top, width, height)
    
    if largest_face_box:
        left, top, width, height = largest_face_box
        # 여유 공간 추가
        padding_width = width * padding_ratio
        padding_height = height * padding_ratio
        padded_left = max(0, left - padding_width)
        padded_top = max(0, top - padding_height)
        padded_right = min(imgWidth, left + width + padding_width)
        padded_bottom = min(imgHeight, top + height + padding_height)
        
        return ori_image, imgWidth, imgHeight, int(padded_left), int(padded_top), int(padded_right - padded_left), int(padded_bottom - padded_top), response
    else:
        return None, None, None, None, None, None, None, None
