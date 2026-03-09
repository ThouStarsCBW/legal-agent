from services.llm_service import generate_response
import re
from typing import Dict, List, Optional

class NLUService:
    """意图识别与语义理解服务"""
    
    def __init__(self):
        pass
    
    def extract_case_elements(self, user_input: str) -> Dict[str, str]:
        """
        案情要素提取：自动识别用户描述中的关键要素
        
        返回要素：
        - time: 时间信息
        - location: 地点信息
        - parties: 当事人信息
        - amount: 标的额
        - legal_relation: 法律关系（借贷、侵权、劳动等）
        - key_facts: 关键事实
        """
        prompt = f"""你是一位专业的法律信息提取专家。请从用户的描述中提取以下关键要素，以JSON格式返回。

用户描述：{user_input}

请提取以下要素（如果某要素未提及，返回空字符串）：
- time: 时间信息（如"2024年1月"、"去年"）
- location: 地点信息（如"北京市朝阳区"、"公司"）
- parties: 当事人信息（如"甲方张三"、"乙方李四"）
- amount: 标的额（如"5000元"、"100万"）
- legal_relation: 法律关系类型（如"借贷关系"、"劳动争议"、"侵权责任"、"合同纠纷"）
- key_facts: 关键事实描述（用一句话概括）

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
                    
            # 尝试解析 JSON
            import json
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "无法解析要素"}
        except Exception as e:
            return {"error": f"提取失败：{str(e)}"}
    
    def generate_followup_questions(self, user_input: str, extracted_elements: Dict) -> List[str]:
        """
        多轮追问引导：当用户提问模糊时，生成追问问题
        """
        prompt = f"""你是一位专业的法律顾问。用户提出了一个法律问题，但可能缺少关键信息。

用户问题：{user_input}

已提取的要素：{extracted_elements}

请分析用户的问题是否缺少关键信息。如果缺少，请生成1-3个追问问题，帮助用户补充信息。
追问要求：
1. 问题要具体、明确
2. 语气要友善、专业
3. 优先追问对案件判断最关键的信息

如果信息已经足够完整，返回空列表。

只返回追问问题的列表，格式如：["问题1", "问题2"]，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            # 尝试解析列表
            list_match = re.search(r'\[.*\]', text, re.DOTALL)
            if list_match:
                import json
                questions = json.loads(list_match.group())
                return questions if questions else []
            else:
                return []
        except Exception as e:
            return []
    
    def convert_legal_terminology(self, user_input: str) -> Dict[str, str]:
        """
        专业术语转换：
        - 将用户的"大白话"转化为法律术语
        - 将法律术语转化为用户易懂的语言
        """
        prompt = f"""你是一位法律术语翻译专家。请完成以下两个任务：

任务1：将用户的"大白话"转化为法律术语
用户描述：{user_input}

任务2：将以下法律术语转化为普通用户易懂的语言
（这个任务将在后续回答时使用）

请返回JSON格式：
{{
    "legal_terms": "将用户描述转化为专业法律术语（如'被辞退' -> '解除劳动合同'）",
    "key_legal_concepts": "识别出的关键法律概念（如'劳动关系'、'违约责任'）"
}}

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            else:
                return {"legal_terms": "", "key_legal_concepts": ""}
        except Exception as e:
            return {"legal_terms": "", "key_legal_concepts": ""}
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, any]:
        """
        综合分析用户意图
        """
        elements = self.extract_case_elements(user_input)
        followup_questions = self.generate_followup_questions(user_input, elements)
        terminology = self.convert_legal_terminology(user_input)
        
        return {
            "extracted_elements": elements,
            "followup_questions": followup_questions,
            "legal_terminology": terminology,
            "is_complete": len(followup_questions) == 0
        }
