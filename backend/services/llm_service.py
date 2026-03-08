from openai import OpenAI
import os
from dotenv import load_dotenv

# ==================== 配置部分 ====================
# 加载 .env 文件中的密钥
load_dotenv()

# 阿里云百炼API 配置
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-sp-65873a7f37604fe888234582b8b8ee14")
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
DEFAULT_MODEL = "qwen3.5-plus"

# 初始化 OpenAI 客户端（兼容阿里云百炼）
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ==================== 工具函数 ====================

def generate_response(prompt, model=DEFAULT_MODEL, stream=False):
    """
    通用文本生成函数
    
    Args:
        prompt: 提示词
        model: 模型名称，默认 qwen3.5-plus
        stream: 是否流式输出，默认 False
    
    Returns:
        str: AI 生成的文本
    """
    try:
        if stream:
            # 流式输出
            messages = [{"role": "user", "content": prompt}]
            full_response = ""
            
            stream_resp = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream_resp:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content
            
            print()  # 换行
            return full_response
        else:
            # 普通输出
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
    
    except Exception as e:
        return f"AI 生成失败，错误信息：{str(e)}"

# ==================== 业务功能函数 ====================

def generate_complaint_text(plaintiff, defendant, outline, stream=False):
    """
    起诉状 AI 扩写
    
    Args:
        plaintiff: 原告信息
        defendant: 被告信息
        outline: 用户诉讼请求提纲
        stream: 是否流式输出，默认 False
    
    Returns:
        str: AI 撰写的起诉状正文
    """
    prompt = f"""你现在是一位热心且专业的中国法律援助律师。你的服务对象是不太懂法律的普通老百姓。
请根据以下用户提供的简单大纲，将其扩写为一份逻辑严密、表述规范的"事实与理由"部分正文。

原告：{plaintiff}
被告：{defendant}
用户诉讼请求提纲：{outline}

要求：
1. 语气专业、客观、不卑不亢，事实陈述清楚。
2. 语言通俗易懂，但必须符合中国民事诉讼法的规范要求。
3. 纯文本输出，不要使用任何 Markdown 格式（如加粗、列表符号）。
4. 结尾必须包含"为维护原告合法权益，特向贵院提起诉讼，望判如所请。"等标准结束语。"""
    
    return generate_response(prompt, DEFAULT_MODEL, stream)

def generate_contract_text(contract_name, party_a, party_b, requirements, stream=False):
    """
    通用合同 AI 扩写
    
    Args:
        contract_name: 合同名称
        party_a: 甲方信息
        party_b: 乙方信息
        requirements: 核心交易条件与业务诉求
        stream: 是否流式输出，默认 False
    
    Returns:
        str: AI 撰写的合同条款
    """
    prompt = f"""你现在是一位专业的中国法务。你的服务对象是需要签订合同的普通人。
请根据用户提供的简单要求，起草一份名为《{contract_name}》的合同正文条款。

甲方：{party_a}
乙方：{party_b}
核心交易条件与业务诉求：{requirements}

要求：
1. 将用户的简单诉求转化为结构清晰的合同条款（如第一条、第二条、违约责任、争议解决等）。
2. 语言通俗易懂，但必须具有法律效力，帮助普通人防范常见风险。
3. 只输出中间的条款正文部分，不要输出合同标题和末尾签字处。
4. 纯文本输出，不要使用任何 Markdown 语法。"""
    
    return generate_response(prompt, DEFAULT_MODEL, stream)

def chat_with_ai(message, conversation_history=None, stream=False):
    """
    通用对话接口（支持多轮对话）
    
    Args:
        message: 用户当前输入
        conversation_history: 历史对话记录，格式为 [{"role": "user/assistant", "content": "..."}]
        stream: 是否流式输出，默认 False
    
    Returns:
        str: AI 回复内容
    """
    try:
        # 构建消息列表
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        if stream:
            # 流式输出
            full_response = ""
            stream_resp = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                stream=True
            )
            
            for chunk in stream_resp:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content
            
            print()  # 换行
            return full_response
        else:
            # 普通输出
            completion = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages
            )
            return completion.choices[0].message.content
    
    except Exception as e:
        return f"对话失败，错误信息：{str(e)}"

# ==================== 示例用法 ====================
if __name__ == "__main__":
    print("="*50)
    print("阿里云百炼法律服务 AI 测试")
    print("="*50)
    
    # 测试 1: 起诉状生成
    print("\n【测试 1】起诉状生成")
    print("-" * 50)
    complaint = generate_complaint_text(
        plaintiff="张三",
        defendant="李四",
        outline="李四欠我 5 万元借款不还，有借条为证",
        stream=True
    )
    print(f"\n生成结果:\n{complaint}")
    
    # 测试 2: 合同生成
    print("\n\n【测试 2】房屋租赁合同生成")
    print("-" * 50)
    contract = generate_contract_text(
        contract_name="房屋租赁合同",
        party_a="王五",
        party_b="赵六",
        requirements="北京市朝阳区三居室，月租 8000 元，押一付三，租期一年",
        stream=False
    )
    print(f"\n生成结果:\n{contract}")
    
    # 测试 3: 多轮对话
    print("\n\n【测试 3】法律咨询对话")
    print("-" * 50)
    history = []
    
    # 第一轮
    msg1 = "离婚需要什么材料？"
    print(f"问:{msg1}")
    reply1 = chat_with_ai(msg1, history, stream=True)
    print(f"答:{reply1}\n")
    history.append({"role": "user", "content": msg1})
    history.append({"role": "assistant", "content": reply1})
    
    # 第二轮
    msg2 = "如果对方不同意呢？"
    print(f"问:{msg2}")
    reply2 = chat_with_ai(msg2, history, stream=False)
    print(f"答:{reply2}")