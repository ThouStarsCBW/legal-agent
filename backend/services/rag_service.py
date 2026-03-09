from services.llm_service import generate_response
import re
from typing import Dict, List

class RAGService:
    """增强检索与知识对齐服务"""
    
    def __init__(self):
        pass
    
    def search_legal_articles(self, user_input: str, legal_terminology: str) -> List[Dict[str, str]]:
        """
        精准法条定位：关联最新的法律法规数据库
        
        返回格式：
        [
            {
                "law_name": "法律名称",
                "article_number": "条目序号",
                "article_content": "法条原文",
                "relevance": "相关性说明"
            }
        ]
        """
        prompt = f"""你是一位专业的法律数据库检索专家。请根据用户的问题，检索相关的法律条文。

用户问题：{user_input}
法律术语：{legal_terminology}

请检索相关的法律条文，重点关注：
1. 《中华人民共和国民法典》
2. 《中华人民共和国劳动合同法》
3. 《中华人民共和国合同法》
4. 《中华人民共和国侵权责任法》
5. 其他相关法律法规

请返回JSON格式，包含最相关的3-5条法条：
[
    {{
        "law_name": "法律名称（如'中华人民共和国民法典'）",
        "article_number": "条目序号（如'第577条'）",
        "article_content": "法条原文内容",
        "relevance": "该法条与用户问题的相关性说明"
    }}
]

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                import json
                articles = json.loads(json_match.group())
                return articles if articles else []
            else:
                return []
        except Exception as e:
            return []
    
    def search_similar_cases(self, user_input: str, legal_terminology: str) -> List[Dict[str, str]]:
        """
        类案智能推荐：检索相似的裁判文书
        
        返回格式：
        [
            {
                "case_title": "案件标题",
                "case_summary": "案件摘要",
                "judgment_tendency": "裁判口径",
                "outcome": "判决结果"
            }
        ]
        """
        prompt = f"""你是一位专业的案例检索专家。请根据用户的问题，检索相似的裁判文书。

用户问题：{user_input}
法律术语：{legal_terminology}

请检索2-3个相似案例，要求：
1. 案情相似度高
2. 具有代表性
3. 总结出该类案件的"裁判口径"和"判决倾向"

请返回JSON格式：
[
    {{
        "case_title": "案件标题（如'张三诉李四劳动争议案'）",
        "case_summary": "案件摘要（简述案情）",
        "judgment_tendency": "裁判口径（法院对此类案件的审理倾向）",
        "outcome": "判决结果（如'支持原告请求'、'驳回起诉'）"
    }}
]

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                import json
                cases = json.loads(json_match.group())
                return cases if cases else []
            else:
                return []
        except Exception as e:
            return []
    
    def get_judicial_interpretations(self, user_input: str, legal_terminology: str) -> List[Dict[str, str]]:
        """
        法理/解释关联：引入最高院的司法解释、指导性案例或专家意见
        """
        prompt = f"""你是一位专业的法律解释专家。请根据用户的问题，检索相关的司法解释或指导性案例。

用户问题：{user_input}
法律术语：{legal_terminology}

请检索相关的：
1. 最高人民法院司法解释
2. 指导性案例
3. 专家意见或学理解释

请返回JSON格式：
[
    {{
        "source": "来源（如'最高人民法院司法解释'、'指导性案例XX号'）",
        "title": "标题",
        "content": "核心内容摘要",
        "relevance": "与用户问题的关联性"
    }}
]

只返回JSON格式，不要其他内容："""
        
        try:
            response = generate_response(prompt)
            text = response
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                import json
                interpretations = json.loads(json_match.group())
                return interpretations if interpretations else []
            else:
                return []
        except Exception as e:
            return []
    
    def retrieve_knowledge(self, user_input: str, legal_terminology: str) -> Dict[str, List[Dict]]:
        """
        综合检索知识库
        """
        articles = self.search_legal_articles(user_input, legal_terminology)
        cases = self.search_similar_cases(user_input, legal_terminology)
        interpretations = self.get_judicial_interpretations(user_input, legal_terminology)
        
        return {
            "legal_articles": articles,
            "similar_cases": cases,
            "judicial_interpretations": interpretations
        }
