from services.llm_service import generate_response
import re
from typing import Dict, List

class ActionGuideService:
    """辅助生成与行动指南服务"""
    
    def __init__(self):
        pass
    
    def generate_document_draft(self, user_input: str, extracted_elements: Dict, doc_type: str) -> Dict[str, str]:
        """
        文书初稿生成：根据问答内容，自动生成针对性的文书草案
        
        doc_type: 'complaint' (起诉状), 'lawyer_letter' (律师函), 'evidence_list' (证据清单)
        """
        if doc_type == 'complaint':
            return self._generate_complaint_draft(user_input, extracted_elements)
        elif doc_type == 'lawyer_letter':
            return self._generate_lawyer_letter_draft(user_input, extracted_elements)
        elif doc_type == 'evidence_list':
            return self._generate_evidence_list_draft(user_input, extracted_elements)
        else:
            return {"error": "不支持的文书类型"}
    
    def _generate_complaint_draft(self, user_input: str, extracted_elements: Dict) -> Dict[str, str]:
        """生成起诉状草案"""
        prompt = f"""你是一位专业的法律文书起草专家。请根据用户提供的信息，起草一份民事起诉状。

用户问题：{user_input}
案情要素：{extracted_elements}

请起草一份标准的民事起诉状，包含以下部分：
1. 原告信息
2. 被告信息
3. 诉讼请求
4. 事实与理由
5. 此致（法院名称）
6. 具状人信息

请返回JSON格式：
{{
    "plaintiff_info": "原告信息",
    "defendant_info": "被告信息",
    "litigation_requests": "诉讼请求（分条列出）",
    "facts_and_reasons": "事实与理由（详细描述）",
    "court_name": "管辖法院",
    "draft_full_text": "完整的起诉状文本"
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
                return {"error": "无法生成起诉状草案"}
        except Exception as e:
            return {"error": f"生成失败：{str(e)}"}
    
    def _generate_lawyer_letter_draft(self, user_input: str, extracted_elements: Dict) -> Dict[str, str]:
        """生成律师函草案"""
        prompt = f"""你是一位专业的法律文书起草专家。请根据用户提供的信息，起草一份律师函。

用户问题：{user_input}
案情要素：{extracted_elements}

请起草一份标准的律师函，包含以下部分：
1. 收函人信息
2. 事由
3. 事实陈述
4. 法律依据
5. 要求
6. 法律后果提示
7. 律师事务所信息

请返回JSON格式：
{{
    "recipient_info": "收函人信息",
    "subject": "事由",
    "facts_statement": "事实陈述",
    "legal_basis": "法律依据",
    "demands": "要求（分条列出）",
    "legal_consequences": "法律后果提示",
    "draft_full_text": "完整的律师函文本"
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
                return {"error": "无法生成律师函草案"}
        except Exception as e:
            return {"error": f"生成失败：{str(e)}"}
    
    def _generate_evidence_list_draft(self, user_input: str, extracted_elements: Dict) -> Dict[str, str]:
        """生成证据清单草案"""
        prompt = f"""你是一位专业的法律文书起草专家。请根据用户提供的信息，起草一份证据清单。

用户问题：{user_input}
案情要素：{extracted_elements}

请起草一份标准的证据清单，列出可能需要的证据材料，包括：
1. 证据名称
2. 证据来源
3. 证明目的
4. 备注

请返回JSON格式：
{{
    "evidence_list": [
        {{
            "evidence_name": "证据名称（如'劳动合同'）",
            "evidence_source": "证据来源（如'公司提供'）",
            "proof_purpose": "证明目的",
            "remarks": "备注"
        }}
    ],
    "collection_tips": "证据收集建议"
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
                return {"error": "无法生成证据清单草案"}
        except Exception as e:
            return {"error": f"生成失败：{str(e)}"}
    
    def generate_action_guide(self, user_input: str, extracted_elements: Dict, legal_analysis: Dict) -> List[Dict[str, str]]:
        """
        维权流程指引：提供清晰的"下一步怎么做"
        """
        prompt = f"""你是一位专业的维权流程指导专家。请根据用户提供的信息，提供详细的维权流程指引。

用户问题：{user_input}
案情要素：{extracted_elements}
法律分析：{legal_analysis}

请提供清晰的维权流程，每一步包括：
1. 步骤名称
2. 具体操作
3. 注意事项
4. 预计时间

请返回JSON格式：
[
    {{
        "step_number": 1,
        "step_name": "步骤名称（如'收集证据'）",
        "specific_actions": "具体操作（详细说明）",
        "precautions": "注意事项",
        "estimated_time": "预计时间（如'1-3天'）",
        "success_criteria": "完成标准"
    }}
]

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                import json
                steps = json.loads(json_match.group())
                return steps if steps else []
            else:
                return []
        except Exception as e:
            return []
    
    def add_source_tagging(self, content: str, sources: Dict) -> str:
        """
        引用溯源：在回答的每一段末尾标注出处
        """
        prompt = f"""你是一位专业的法律引用标注专家。请在回答的每一段末尾标注出处。

原始内容：{content}

来源信息：
- 法条来源：{sources.get('legal_articles', [])}
- 案例来源：{sources.get('similar_cases', [])}
- 司法解释：{sources.get('judicial_interpretations', [])}

请在每一段末尾添加引用标注，格式如：
[来源：《民法典》第577条]

只返回添加了引用标注的内容，不要其他说明："""
        
        try:
            response = generate_response(prompt)
            return response
        except Exception as e:
            return content
    
    def generate_action_package(self, user_input: str, extracted_elements: Dict, legal_analysis: Dict, sources: Dict) -> Dict[str, any]:
        """
        生成完整的行动指南包
        """
        action_guide = self.generate_action_guide(user_input, extracted_elements, legal_analysis)
        
        complaint_draft = self.generate_document_draft(user_input, extracted_elements, 'complaint')
        lawyer_letter_draft = self.generate_document_draft(user_input, extracted_elements, 'lawyer_letter')
        evidence_list_draft = self.generate_document_draft(user_input, extracted_elements, 'evidence_list')
        
        return {
            "action_guide": action_guide,
            "document_drafts": {
                "complaint": complaint_draft,
                "lawyer_letter": lawyer_letter_draft,
                "evidence_list": evidence_list_draft
            },
            "sources": sources
        }
