import os
from google import genai

# 1. 显式定义 Key，确保没有奇怪的字符
MY_API_KEY = "AIzaSyBJ0WIE0xOp71kQdBPwMq94LJ56zySS7Xo"

try:
    client = genai.Client(api_key=MY_API_KEY)

    # 2. 启动对话，system_instruction 放在 config 里
    # 注意：system_instruction 是给 AI 的设定，内容可以是中文
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config={
            'system_instruction': '你是一个专业的法律助手，请用中文回答。',
        }
    )

    print("--- 已成功连接 Gemini，可以开始法律咨询（输入 quit 退出） ---")

    while True:
        user_input = input("用户: ")
        if user_input.lower() in ['quit', 'exit']:
            break

        # 3. 发送消息，context 会自动维护在 chat 对象中
        response = chat.send_message(user_input)
        print(f"AI: {response.text}\n")

except Exception as e:
    print(f"检测到异常：{e}")