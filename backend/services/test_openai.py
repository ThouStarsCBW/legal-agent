from openai import OpenAI

# ==================== 配置部分 ====================
API_KEY = "sk-sp-65873a7f37604fe888234582b8b8ee14"
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
DEFAULT_MODEL = "qwen3.5-plus"

# 常用模型列表（Coding Plan 支持的模型）
AVAILABLE_MODELS = [
    "qwen3.5-plus",
    "qwen3-max-2026-01-23",
    "qwen3-coder-next",
    "qwen3-coder-plus",
    "glm-5",
    "glm-4.7",
    "kimi-k2.5",
    "MiniMax-M2.5"
]

# ==================== 工具函数 ====================

def print_streaming(text, end=''):
    """流式打印文本，逐字显示"""
    print(text, end=end, flush=True)

def stream_response(client, model, messages):
    """流式调用 API 并逐字输出"""
    full_response = ""
    
    # 创建流式请求
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True  # 开启流式输出
    )
    
    # 逐块处理响应
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print_streaming(content)  # 逐字打印
            full_response += content
    
    print()  # 换行
    return full_response

# ==================== 功能演示 ====================

def demo_model_list():
    """1. 输出可用模型列表"""
    print("\n" + "="*50)
    print("【功能 1】可用模型列表")
    print("="*50)
    print("\n⚠️  说明：阿里云百炼 Coding Plan 不支持通过 API 获取模型列表")
    print("   以下是官方文档中列出的常用模型：\n")
    
    print(f"当前使用模型：{DEFAULT_MODEL}")
    print(f"\n支持的模型列表:")
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        print(f"  {i}. {model}")
    
    print("\n💡 提示：如需查看完整模型列表，请访问：")
    print("   https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope")

def demo_multi_round_conversation(max_rounds=5):
    """2. 创建多轮对话（限定轮数）"""
    print("\n" + "="*50)
    print(f"【功能 2】多轮对话演示（最多{max_rounds}轮）")
    print("="*50)
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        # 初始化对话历史
        messages = []
        
        print("\n💬 开始多轮对话（输入'quit'退出）\n")
        
        while len(messages) < max_rounds * 2:  # 每轮包含用户和助手各一条消息
            user_input = input("你：")
            if user_input.lower() == 'quit':
                break
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 流式调用并输出
            print("\n助手:", end='', flush=True)
            assistant_reply = stream_response(client, DEFAULT_MODEL, messages)
            print()  # 空行
            
            # 添加助手回复到历史记录
            messages.append({"role": "assistant", "content": assistant_reply})
            
            # 如果超过最大轮数，移除最早的对话（保留最近 max_rounds 轮）
            if len(messages) > max_rounds * 2:
                messages = messages[-max_rounds * 2:]
        
        print(f"\n对话结束，共进行了 {len(messages)//2} 轮")
        
    except Exception as e:
        print(f"错误：{e}")

def demo_no_thinking():
    """3. 关闭深度思考"""
    print("\n" + "="*50)
    print("【功能 3】关闭深度思考")
    print("="*50)
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        question = "请解释什么是量子纠缠？"
        print(f"\n问题：{question}")
        print("\n（已关闭深度思考模式）\n")
        
        print("回答:", end='', flush=True)
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": question}
            ],
            # 关闭深度思考的参数
            extra_body={
                "enable_thinking": False
            }
        )
        
        # 如果需要流式输出，可以使用：
        # answer = stream_response(client, DEFAULT_MODEL, [{"role": "user", "content": question}])
        # 但这里为了演示关闭思考的效果，使用普通输出
        print(completion.choices[0].message.content)
        
        # 检查是否有思考内容
        if hasattr(completion.choices[0].message, 'reasoning_content'):
            print(f"\n[思考内容已隐藏]")
        
    except Exception as e:
        print(f"错误：{e}")

def demo_prompt_engineering():
    """4. 提示词工程演示"""
    print("\n" + "="*50)
    print("【功能 4】提示词工程演示")
    print("="*50)
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        # 场景 1: 设定专业角色
        print("\n【场景 1】专业角色扮演")
        print("-" * 50)
        
        system_prompt = """你是一位经验丰富的法律顾问，专门处理民事纠纷。
请用专业但通俗易懂的语言回答问题，并引用相关法律条文。"""
        
        user_question = "邻居装修噪音扰民，我该怎么办？"
        
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ]
        )
        
        print(f"问题：{user_question}")
        print(f"\n回答:\n{completion.choices[0].message.content}")
        
        # 流式输出版本（可选）:
        # print(f"问题：{user_question}")
        # print(f"\n回答:\n", end='', flush=True)
        # stream_response(client, DEFAULT_MODEL, [
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": user_question}
        # ])
        
        # 场景 2: 结构化输出
        print("\n\n【场景 2】要求结构化输出")
        print("-" * 50)
        
        structured_prompt = """请分析以下案例，并按 JSON 格式输出：
{
  "案件类型": "",
  "关键事实": [],
  "适用法律": [],
  "建议措施": []
}

案例：小明在网购商品后发现质量问题，要求退货但商家拒绝。"""
        
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": structured_prompt}
            ]
        )
        
        print(f"回答:\n{completion.choices[0].message.content}")
        
        # 场景 3: 思维链引导
        print("\n\n【场景 3】思维链引导（逐步推理）")
        print("-" * 50)
        
        cot_prompt = """请逐步分析这个问题：
1. 首先识别问题的关键点
2. 然后分析相关法律规定
3. 最后给出具体建议

问题：公司未签订劳动合同就辞退员工，员工如何维权？"""
        
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": cot_prompt}
            ]
        )
        
        print(f"回答:\n{completion.choices[0].message.content}")
        
    except Exception as e:
        print(f"错误：{e}")

def demo_limited_conversation():
    """5. 限定对话轮数的完整示例"""
    print("\n" + "="*50)
    print("【功能 5】限定对话轮数（3 轮）演示")
    print("="*50)
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        # 设定系统角色
        system_prompt = "你是一个简洁的助手，每次回答不超过 50 字。"
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        max_rounds = 3
        questions = [
            "什么是人工智能？",
            "它有哪些应用场景？",
            "未来发展趋势是什么？"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n第{i}轮:")
            print(f"问:{question}")
            
            messages.append({"role": "user", "content": question})
            
            # 流式输出
            print("答:", end='', flush=True)
            answer = stream_response(client, DEFAULT_MODEL, messages)
            print()  # 空行
            
            messages.append({"role": "assistant", "content": answer})
            
            # 保持对话历史在限定轮数内
            # system 消息始终保留，只限制对话轮数
            if len(messages) > (max_rounds * 2 + 1):  # +1 是 system 消息
                messages = [messages[0]] + messages[-max_rounds * 2:]
        
        print(f"\n✓ 完成{max_rounds}轮对话演示")
        
    except Exception as e:
        print(f"错误：{e}")

# ==================== 主函数 ====================
if __name__ == "__main__":
    print("\n" + "🤖 " + "="*48)
    print("   阿里云百炼 OpenAI兼容接口功能演示")
    print("="*50 + " 🤖\n")
    
    # 选择要演示的功能
    print("请选择要演示的功能:")
    print("1. 获取模型列表")
    print("2. 多轮对话（交互式）")
    print("3. 关闭深度思考")
    print("4. 提示词工程")
    print("5. 限定对话轮数（自动演示）")
    print("6. 运行所有演示")
    
    choice = input("\n请输入选项 (1-6): ").strip()
    
    functions = {
        '1': demo_model_list,
        '2': demo_multi_round_conversation,
        '3': demo_no_thinking,
        '4': demo_prompt_engineering,
        '5': demo_limited_conversation,
        '6': None  # 特殊处理
    }
    
    if choice == '6':
        # 运行所有演示
        demo_model_list()
        input("\n按回车键继续下一个演示...")
        demo_no_thinking()
        input("\n按回车键继续下一个演示...")
        demo_prompt_engineering()
        input("\n按回车键继续下一个演示...")
        demo_limited_conversation()
        input("\n按回车键继续下一个演示...")
        demo_multi_round_conversation()
    elif choice in functions:
        functions[choice]()
    else:
        print("无效的选项！")