# GenAI Gallery

This repository is a sample project that utilizes [Amazon Bedrock](https://aws.amazon.com/bedrock/) for generative AI, to create images of historical figures. It then uses a SageMaker Endpoint to synthesize these images with users' selfie photos, producing composite results. This showcase demonstrates the integration of various AWS AI services for creative image generation and manipulation.

## Architecture

Key Components:

- [AWS Amplify](https://aws.amazon.com/amplify/): Provides frontend application hosting (using React).
- [Amazon API Gateway](https://aws.amazon.com/api-gateway/) + [AWS Lambda](https://aws.amazon.com/lambda/): Used as backend API endpoints for image retrieval and upload.
- [Amazon Bedrock](https://aws.amazon.com/bedrock/): A managed service that utilizes foundation models through APIs. It uses the Amazon Titan Image Generator model for image generation and the Claude 3.0 Sonnet model for descriptions.
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/): Deploys the necessary model as an Endpoint to process image synthesis requests.
- [Amazon Rekognition](https://aws.amazon.com/rekognition/): Detects faces in images and videos, and crops the relevant facial areas.

## Deploy

GenAI Gallery를 배포하려면 다음 단계를 따르세요:

### Prerequisites

1. Before you begin, ensure you have met the following requirements:

    * You have installed the latest version of [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
    * You have an [AWS account](https://aws.amazon.com/free/)
    * You have the necessary permissions to create and manage AWS resources
    * You have a [GitHub account](https://github.com/) and a personal access token with appropriate permissions

2. Clone the repository:
    ```
    https://github.com/raphael-shin/my-aws-cdk-sample.git
    ```

### Step 1: Deploy Backend

1. Move backend directory:
    ```
    cd backend
   ```

2. Create a virtual environment:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
   ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Configure your AWS credentials:
    ```
    aws configure
    ```

5. Update the `cdk.context.json` file with your aws region, and other configuration details.
    ```
    {
        "s3_base_bucket_name": "genai-gallery",
        "s3_base_images_path": "images/base/",
        "s3_face_images_path": "images/face/",
        "s3_masked_face_images_path": "images/masked-face/",
        "s3_swapped_face_images_path": "images/swapped-face/",
        "s3_result_images_path": "images/result/",
        "pillow_layer_arn": "arn:aws:lambda:{your-aws-region}:770693421928:layer:Klayers-p38-Pillow:10",
        "numpy_layer_arn": "arn:aws:lambda:{your-aws-region}:770693421928:layer:Klayers-p38-numpy:13"
    }
    ```

6. Check CDK deploy outputs:

### Step 2: Run Frontend Application

1. backend를 배포합니다.
2. 배포가 완료되면 (약 30분 소요) 다음과 유사한 출력을 받게 됩니다:

   ```
   Amazon API Gateway Endpoint URL: https://xxxxxxxxxx.execute-api.xxxxxxxxxx.amazonaws.com/prod
   ```

3. frontend 폴더의 `.env` 파일에서 `REACT_APP_API_ENDPOINT={your backend Amazon API Gateway endpoint url}`의 `{your backend Amazon API Gateway endpoint url}` 부분을 위의 API Gateway Endpoint URL로 변경합니다.
4. backend 디렉토리에 있었을 경우 아래의 명령어를 통하여 frontend 디렉토리로 이동합니다.
    ```
        cd ../frontend
    ```
5. 디펜던시를 설치합니다.
    ```
        npm install
    ```
6. 아래의 명령어를 통해서 애플리케이션을 실행합니다.
    ```
        npm start
    ```

## Contacts

- [Chulwoo Choi](https://github.com/prorhap)
- [Jinwoo Park](https://github.com/jinuland)
- [Jungseob Shin](https://github.com/raphael-shin)
- [Seongjin Ahn](https://github.com/tjdwlsdlaek)
- [Kihoon Kwon](https://github.com/kyoonkwon)
- [Jisoo Min](https://github.com/Jisoo-Min)
- [Hyeryeong Joo](https://github.com/HyeryeongJoo)

## Contributors

[![genai-gallery contributors](https://contrib.rocks/image?repo=raphael-shin/my-aws-cdk-sample&max=1000)](https://github.com/raphael-shin/my-aws-cdk-sample/graphs/contributors)

## License

This library is licensed under the MIT-0 License. See [the LICENSE file](./LICENSE).