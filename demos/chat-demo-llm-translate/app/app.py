import streamlit as st
import time
import boto3
import json
import os
from urllib.parse import urlparse

AWS_REGION = "us-east-1"
bedrock = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)

def get_current_time():
    return time.strftime("%H:%M:%S")

def translate_to_japanese(text, model_id, temperature, top_p, top_k, max_tokens):
    system_prompt = """
    You are a professional translator. Your task is to accurately translate the given Korean text into Japanese. Present only the translation result without any additional explanations or comments. Do not use quotation marks or any other symbols in the translated text.
    """

    body = json.dumps({
        "anthropic_version": "",
        "messages": [{"role": "user", "content": f"Please translate the following text into Japanese: {text}"}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "system": system_prompt,
    })
    response = bedrock.invoke_model(
        modelId=model_id,
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def main():
    # URL에서 사용자 정보 추출
    user = st.query_params.get("user", "default")

    print(f"User: {user}")

    st.title("실시간 번역 채팅 애플리케이션")
    # 사이드바에 AI 모델 및 파라미터 설정 추가
    st.sidebar.header("AI 모델 및 파라미터 설정")

    model_options = {
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "Claude 3.5 Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "Claude 3 Opus": "anthropic.claude-3-opus-20240229-v1:0"
    }

    selected_model = st.sidebar.selectbox("AI 모델 선택", list(model_options.keys()))
    model_id = model_options[selected_model]

    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
    top_p = st.sidebar.slider("Top P", 0.0, 1.0, 0.9, 0.1)
    top_k = st.sidebar.slider("Top K", 1, 500, 250, 1)
    max_tokens = st.sidebar.slider("Max Tokens", 200, 4096, 1000, 100)

    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    user_icons = {
        "user1": './user1.webp',
        "user2": './user2.webp',
        "default": './default.webp'
    }

    # 현재 사용자의 아바타 선택
    current_user_icon = user_icons.get(user, user_icons["default"])

    # 채팅 내역 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=current_user_icon):
            st.markdown(f"{message['content']}")

    # 채팅 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 표시
        st.chat_message("user", avatar=current_user_icon).markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt, "time": get_current_time()})

        # 일본어로 번역
        japanese_translation = translate_to_japanese(prompt, model_id, temperature, top_p, top_k, max_tokens)
        with st.chat_message("assistant"):
            st.markdown(japanese_translation)
        st.session_state.messages.append({"role": "assistant", "content": japanese_translation, "time": get_current_time()})

if __name__ == "__main__":
    main()
