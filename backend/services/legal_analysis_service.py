from services.llm_service import generate_response
import re
from typing import Dict, List
from datetime import datetime, timedelta

class LegalAnalysisService:
    """逻辑推理与初步法律分析服务"""
    
    def __init__(self):
        pass
    
    def analyze_rights_obligations(self, user_input: str, extracted_elements: Dict, legal_articles: List[Dict]) -> Dict[str, str]:
        """
        权利义务关系分析：自动梳理双方的合同义务或法律责任
        """
        prompt = f"""你是一位专业的法律关系分析专家。请根据用户提供的信息，分析双方的权利义务关系。

用户问题：{user_input}
案情要素：{extracted_elements}
相关法条：{legal_articles}

请分析：
1. 各方的权利是什么
2. 各方的义务是什么
3. 是否存在违约或侵权行为
4. 责任如何划分

请返回JSON格式：
{{
    "party_a_rights": "甲方（或原告）的权利",
    "party_a_obligations": "甲方（或原告）的义务",
    "party_b_rights": "乙方（或被告）的权利",
    "party_b_obligations": "乙方（或被告）的义务",
    "breach_analysis": "是否存在违约或侵权行为及分析",
    "responsibility_distribution": "责任划分建议"
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
                return {"error": "无法分析权利义务关系"}
        except Exception as e:
            return {"error": f"分析失败：{str(e)}"}
    
    def assess_win_probability(self, user_input: str, extracted_elements: Dict, similar_cases: List[Dict]) -> Dict[str, any]:
        """
        胜诉/风险预判：基于已有的事实和法条，给出初步的风险评估
        """
        prompt = f"""你是一位专业的法律风险评估专家。请根据用户提供的信息，给出胜诉概率和风险评估。

用户问题：{user_input}
案情要素：{extracted_elements}
相似案例：{similar_cases}

请分析：
1. 胜诉概率（高/中/低）
2. 证据不足的风险点
3. 法律适用的风险点
4. 诉讼成本与收益分析

请返回JSON格式：
{{
    "win_probability": "胜诉概率（高/中/低）",
    "probability_score": "概率评分（0-100）",
    "evidence_risks": ["证据风险点1", "证据风险点2"],
    "legal_risks": ["法律适用风险点1", "法律适用风险点2"],
    "cost_benefit_analysis": "诉讼成本与收益分析",
    "key_success_factors": ["关键成功因素1", "关键成功因素2"]
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
                return {"error": "无法评估胜诉概率"}
        except Exception as e:
            return {"error": f"评估失败：{str(e)}"}
    
    def check_statute_of_limitations(self, user_input: str, extracted_elements: Dict) -> Dict[str, any]:
        """
        时效提醒：自动检测是否存在超过诉讼时效或仲裁时效的风险
        """
        prompt = f"""你是一位专业的诉讼时效专家。请根据用户提供的信息，检查是否存在超过诉讼时效的风险。

用户问题：{user_input}
案情要素：{extracted_elements}

请分析：
1. 诉讼时效类型（一般3年、特殊1年或2年等）
2. 诉讼时效起算点
3. 是否存在时效中断或中止的情形
4. 是否超过诉讼时效
5. 如果即将超过，给出提醒

请返回JSON格式：
{{
    "limitation_type": "诉讼时效类型（如'一般诉讼时效3年'、'劳动仲裁时效1年'）",
    "limitation_period": "时效期间",
    "start_date": "时效起算点（从事件发生之日起）",
    "is_expired": "是否超过时效（true/false）",
    "days_remaining": "剩余天数（如果未过期）",
    "days_overdue": "已过期天数（如果已过期）",
    "interruption_factors": ["可能的中断或中止因素"],
    "recommendation": "时效方面的建议"
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
                return {"error": "无法检查诉讼时效"}
        except Exception as e:
            return {"error": f"检查失败：{str(e)}"}
    
    def perform_legal_analysis(self, user_input: str, extracted_elements: Dict, legal_articles: List[Dict], similar_cases: List[Dict]) -> Dict[str, any]:
        """
        综合法律分析
        """
        rights_obligations = self.analyze_rights_obligations(user_input, extracted_elements, legal_articles)
        win_probability = self.assess_win_probability(user_input, extracted_elements, similar_cases)
        statute_check = self.check_statute_of_limitations(user_input, extracted_elements)
        
        return {
            "rights_obligations_analysis": rights_obligations,
            "win_probability_assessment": win_probability,
            "statute_of_limitations_check": statute_check
        }
