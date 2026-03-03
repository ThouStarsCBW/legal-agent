import google.generativeai as genai
import os
from dotenv import load_dotenv

# 加载 .env 文件中的密钥
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)

# 初始化模型
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_complaint_text(plaintiff, defendant, outline):
    """起诉状 AI 扩写"""
    prompt = f"""你现在是一位热心且专业的中国法律援助律师。你的服务对象是不太懂法律的普通老百姓。
请根据以下用户提供的简单大纲，将其扩写为一份逻辑严密、表述规范的“事实与理由”部分正文。

原告：{plaintiff}
被告：{defendant}
用户诉讼请求提纲：{outline}

要求：
1. 语气专业、客观、不卑不亢，事实陈述清楚。
2. 语言通俗易懂，但必须符合中国民事诉讼法的规范要求。
3. 纯文本输出，不要使用任何 Markdown 格式（如加粗、列表符号）。
4. 结尾必须包含“为维护原告合法权益，特向贵院提起诉讼，望判如所请。”等标准结束语。
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 撰写失败，错误信息：{str(e)}"

def generate_contract_text(contract_name, party_a, party_b, requirements):
    """通用合同 AI 扩写"""
    prompt = f"""你现在是一位专业的中国法务。你的服务对象是需要签订合同的普通人。
请根据用户提供的简单要求，起草一份名为《{contract_name}》的合同正文条款。

甲方：{party_a}
乙方：{party_b}
核心交易条件与业务诉求：{requirements}

要求：
1. 将用户的简单诉求转化为结构清晰的合同条款（如第一条、第二条、违约责任、争议解决等）。
2. 语言通俗易懂，但必须具有法律效力，帮助普通人防范常见风险。
3. 只输出中间的条款正文部分，不要输出合同标题和末尾签字处。
4. 纯文本输出，不要使用任何 Markdown 语法。
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 撰写失败，错误信息：{str(e)}"