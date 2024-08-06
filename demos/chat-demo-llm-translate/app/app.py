import streamlit as st
import time
import boto3
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os
from datetime import datetime, timedelta

# AWS 설정
AWS_REGION = "us-east-1"
bedrock = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# 환경 변수에서 테이블 이름을 가져옴. 환경 변수가 없으면 기본값 사용
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "ChatMessages")

def get_current_time():
    return datetime.utcnow().isoformat()

def save_message(room_id, message):
    table = dynamodb.Table(TABLE_NAME)
    timestamp = get_current_time()
    try:
        table.put_item(
            Item={
                'room_id': room_id,
                'timestamp': timestamp,
                'user': message['user'],
                'content': message['content'],
                'translated': message['translated'],
                'message_type': message['message_type']
            }
        )
        return timestamp
    except ClientError as e:
        st.error(f"Error saving message: {e}")
        return None

def get_new_messages(room_id, last_timestamp):
    table = dynamodb.Table(TABLE_NAME)
    try:
        response = table.query(
            KeyConditionExpression=Key('room_id').eq(room_id) & Key('timestamp').gt(last_timestamp),
            ScanIndexForward=True
        )
        return response['Items']
    except ClientError as e:
        st.error(f"Error retrieving messages: {e}")
        return []

def translate_message(text, source_lang, target_lang, model_id, temperature, top_p, top_k, max_tokens):
    system_prompt = f"You are a professional translator. Translate the following {source_lang} text to {target_lang}. Provide only the translation without any additional comments."
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": f"Translate this {source_lang} text to {target_lang}: {text}"
            }
        ]
    })

    try:
        response = bedrock.invoke_model(body=body, modelId=model_id)
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    except Exception as e:
        st.error(f"Translation error: {e}")
        return "Translation error occurred. Please try again later."

def main():
    st.title("실시간 번역 채팅 애플리케이션")
    st.sidebar.text(f"사용 중인 DynamoDB 테이블: {TABLE_NAME}")

    # URL에서 사용자 정보 추출
    query_params = st.query_params
    current_user = query_params.get("user", "default")
    room_id = query_params.get("room", "default_room")

    # 사이드바에 AI 모델 및 파라미터 설정 추가
    st.sidebar.header("AI 모델 및 파라미터 설정")
    model_options = {
        "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Claude 3.5 Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "Claude 3 Opus": "anthropic.claude-3-opus-20240229-v1:0"
    }
    selected_model = st.sidebar.selectbox("AI 모델 선택", list(model_options.keys()))
    model_id = model_options[selected_model]
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
    top_p = st.sidebar.slider("Top P", 0.0, 1.0, 0.9, 0.1)
    top_k = st.sidebar.slider("Top K", 1, 500, 250, 1)
    max_tokens = st.sidebar.slider("Max Tokens", 200, 4096, 1000, 100)

    user_icons = {
        "user1": './user1.webp',
        "user2": './user2.webp'
    }

    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'last_timestamp' not in st.session_state:
        st.session_state.last_timestamp = (datetime.utcnow() - timedelta(hours=1)).isoformat()

    # 사용자별 UI 렌더링
    if current_user == "user1":  # 한국인 사용자
        st.header("한국어 채팅")
        input_lang, output_lang = "한국어", "일본어"
        input_placeholder = "한국어 메시지 입력"
        send_button = "전송"
        user_label = "<한국인>"
        other_user_label = "<일본인>"
        translator_label = "<번역봇>"
    elif current_user == "user2":  # 일본인 사용자
        st.header("日本語チャット")
        input_lang, output_lang = "일본어", "한국어"
        input_placeholder = "日本語メッセージを入力"
        send_button = "送信"
        user_label = "<日本人>"
        other_user_label = "<韓国人>"
        translator_label = "<翻訳ボット>"
    else:
        st.error("Invalid user. Please use ?user=user1 or ?user=user2 in the URL.")
        return

    # 메시지 입력
    user_input = st.text_input(input_placeholder)
    if st.button(send_button):
        if user_input:
            # 번역
            translated = translate_message(user_input, input_lang, output_lang, model_id, temperature, top_p, top_k, max_tokens)
            
            # 사용자 메시지 저장
            user_message = {
                "user": current_user,
                "content": user_input,
                "translated": translated,
                "message_type": "user"
            }
            timestamp = save_message(room_id, user_message)
            if timestamp:
                st.session_state.last_timestamp = timestamp
                st.session_state.messages.append(user_message)

            # 번역 봇 메시지 저장
            bot_message = {
                "user": "translator",
                "content": translated,
                "translated": user_input,
                "message_type": "bot"
            }
            timestamp = save_message(room_id, bot_message)
            if timestamp:
                st.session_state.last_timestamp = timestamp
                st.session_state.messages.append(bot_message)

    # 새 메시지 확인 및 UI 업데이트
    new_messages = get_new_messages(room_id, st.session_state.last_timestamp)
    if new_messages:
        st.session_state.messages.extend(new_messages)
        st.session_state.last_timestamp = new_messages[-1]['timestamp']
        st.rerun()

    # 채팅 내역 표시
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message['message_type'] == 'user':
                if message['user'] == current_user:
                    with st.chat_message("user", avatar=user_icons[current_user]):
                        st.write(f"{user_label} {message['content']}")
                        st.write(f"{translator_label} {message['translated']}")
                else:
                    with st.chat_message("assistant", avatar=user_icons[message['user']]):
                        st.write(f"{other_user_label} {message['translated']}")

    # 주기적으로 새 메시지 확인
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()