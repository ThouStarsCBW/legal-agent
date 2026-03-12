from services.llm_service import generate_response
import re
from typing import Dict, List, Optional

# 全局上下文存储（实际生产环境建议使用 Redis 等）
conversation_contexts = {}

class NLUService:
    """意图识别与语义理解服务"""
    
    def __init__(self):
        self.max_followup_rounds = 3  # 最多追问 3 轮
    
    def check_direct_answer_intent(self, user_input: str) -> bool:
        """
        检查用户是否要求直接回答（不再追问）
        检测关键词如："直接回答"、"没有更多信息了"、"快点说"、"别问了"等
        """
        direct_keywords = [
            "直接回答", "直接说", "直接告诉", "别问了", "不要问",
            "没有更多信息", "就这些", "就这么多了", "快点说",
            "赶紧说", "废话少说", "直接给结果", "直接分析",
            "不用问", "别再问", "停止提问", "开始回答"
        ]
        
        user_input_lower = user_input.lower()
        for keyword in direct_keywords:
            if keyword in user_input_lower:
                return True
        return False
    
    def extract_case_elements(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, str]:
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
        # 合并上下文信息
        full_input = user_input
        if context and context.get('history_elements'):
            # 将历史提取的要素合并到当前输入中
            history = context['history_elements']
            merged_info = []
            for key, value in history.items():
                if value and isinstance(value, str) and value.strip():
                    merged_info.append(f"{key}: {value}")
            if merged_info:
                full_input = user_input + "\n已知信息：" + ", ".join(merged_info)
        
        prompt = f"""你是一位专业的法律信息提取专家。请从用户的描述中提取以下关键要素，以 JSON 格式返回。

用户描述：{full_input}

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
    
    def generate_followup_questions(self, user_input: str, extracted_elements: Dict, context: Optional[Dict] = None) -> List[str]:
        """
        多轮追问引导：当用户提问模糊时，生成追问问题
        考虑上下文和追问次数限制
        """
        # 检查追问次数
        if context:
            followup_count = context.get('followup_count', 0)
            if followup_count >= self.max_followup_rounds:
                # 超过最大追问次数，不再追问
                return []
        
        # 计算还需要追问的关键信息
        critical_missing = self._get_critical_missing_info(extracted_elements)
        
        if not critical_missing:
            # 关键信息已足够完整
            return []
        
        prompt = f"""你是一位专业的法律顾问。用户提出了一个法律问题，但可能缺少关键信息。

用户问题：{user_input}

已提取的要素：{extracted_elements}

缺失的关键信息：{critical_missing}

请分析用户的问题是否缺少关键信息。如果缺少，请生成 1-2 个最关键的追问问题，帮助用户补充信息。
追问要求：
1. 问题要具体、明确，优先追问对案件判断最关键的信息
2. 语气要友善、专业
3. 每次只追问最重要的 1-2 个问题
4. 如果信息已经基本完整，返回空列表

只返回追问问题的列表，格式如：["问题 1", "问题 2"]，不要其他内容："""
        
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
    
    def _get_critical_missing_info(self, extracted_elements: Dict) -> List[str]:
        """
        获取缺失的关键信息列表
        根据法律关系类型判断哪些信息是必须的
        """
        critical_fields = {
            '借贷关系': ['amount', 'time', 'parties'],
            '劳动争议': ['parties', 'time', 'legal_relation'],
            '租赁合同': ['parties', 'amount', 'location'],
            '合同纠纷': ['parties', 'amount', 'legal_relation'],
            '侵权责任': ['parties', 'location', 'key_facts']
        }
        
        legal_type = extracted_elements.get('legal_relation', '')
        required_fields = critical_fields.get(legal_type, ['parties', 'key_facts'])
        
        missing = []
        for field in required_fields:
            if not extracted_elements.get(field) or extracted_elements[field].strip() == '':
                missing.append(field)
        
        return missing[:3]  # 最多返回 3 个最关键的缺失字段
    
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
    
    def analyze_user_intent(self, user_input: str, conversation_id: Optional[str] = None) -> Dict[str, any]:
        """
        综合分析用户意图
        Args:
            user_input: 用户输入
            conversation_id: 会话 ID，用于追踪上下文
        """
        # 获取或创建会话上下文
        if not conversation_id:
            conversation_id = "default"
        
        if conversation_id not in conversation_contexts:
            conversation_contexts[conversation_id] = {
                'history_elements': {},
                'followup_count': 0,
                'conversation_history': []
            }
        
        context = conversation_contexts[conversation_id]
        
        # 1. 检查用户是否要求直接回答
        if self.check_direct_answer_intent(user_input):
            # 用户明确要求直接回答，跳过追问
            elements = self.extract_case_elements(user_input, context)
            terminology = self.convert_legal_terminology(user_input)
            
            # 重置追问计数
            context['followup_count'] = 0
            
            return {
                "extracted_elements": elements,
                "followup_questions": [],
                "legal_terminology": terminology,
                "is_complete": True,
                "direct_answer_requested": True
            }
        
        # 2. 正常流程：提取要素
        elements = self.extract_case_elements(user_input, context)
        
        # 3. 更新上下文中的历史要素
        for key, value in elements.items():
            if value and isinstance(value, str) and value.strip():
                context['history_elements'][key] = value
        
        # 4. 生成追问问题（会考虑追问次数限制）
        followup_questions = self.generate_followup_questions(user_input, elements, context)
        
        # 5. 如果有追问，增加追问计数
        if followup_questions:
            context['followup_count'] += 1
        else:
            # 如果没有追问，说明信息已完整，重置计数
            context['followup_count'] = 0
        
        # 6. 术语转换
        terminology = self.convert_legal_terminology(user_input)
        
        # 7. 记录对话历史
        context['conversation_history'].append({
            'user_input': user_input,
            'elements': elements,
            'followup_questions': followup_questions
        })
        
        # 保留最近 10 轮对话
        if len(context['conversation_history']) > 10:
            context['conversation_history'] = context['conversation_history'][-10:]
        
        return {
            "extracted_elements": elements,
            "followup_questions": followup_questions,
            "legal_terminology": terminology,
            "is_complete": len(followup_questions) == 0,
            "direct_answer_requested": False,
            "followup_count": context['followup_count'],
            "max_followup_reached": context['followup_count'] >= self.max_followup_rounds
        }
