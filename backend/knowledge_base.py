#!/usr/bin/env python3
"""
知识库管理模块 - 加载和检索法律文档（Word 版本）
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import json
from docx import Document

class KnowledgeBase:
    """法律知识库"""
    
    def __init__(self, base_path: str = None):
        # 智能路径处理：law_word 文件夹与 backend 同级
        if base_path is None:
            # law_word 在 backend 的父目录（与 backend 同级）
            self.base_path = Path(__file__).parent.parent / "law_word"
        else:
            self.base_path = Path(base_path)
        self.documents = []
        self.stats = {
            '宪法': 0,
            '法律': 0,
            '行政法规': 0,
            '监察法规': 0,
            '司法解释': 0
        }
        self.load_documents()
    
    def load_documents(self):
        """加载所有法律文档（Word 版本）"""
        print("正在加载法律 Word 文档...")
            
        if not self.base_path.exists():
            print(f"警告：文档目录不存在 {self.base_path}")
            return
            
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.docx') and not file.startswith('~$'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.base_path)
                        
                    # 读取 Word 文档内容
                    try:
                        content = self._read_word_content(file_path)
                    except Exception as e:
                        print(f"  读取失败：{file_path} - {e}")
                        continue
                        
                    # 提取标题（从文件名或文档内容）
                    title = self._extract_title_from_word(content, file)
                        
                    # 提取发布日期
                    publish_date = self._extract_date(file)
                        
                    # 分类
                    category = self._categorize(str(rel_path))
                    self.stats[category] += 1
                        
                    doc = {
                        'id': len(self.documents),
                        'title': title,
                        'category': category,
                        'file_path': str(file_path),
                        'rel_path': str(rel_path),
                        'publish_date': publish_date,
                        'content': content,
                        'content_preview': content[:500] + '...' if len(content) > 500 else content
                    }
                        
                    self.documents.append(doc)
            
        print(f"已加载 {len(self.documents)} 个法律 Word 文档")
        for cat, count in self.stats.items():
            if count > 0:
                print(f"  {cat}: {count}")
    
    def _read_word_content(self, file_path: Path) -> str:
        """读取 Word 文档内容"""
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs)
    
    def _extract_title_from_word(self, content: str, filename: str) -> str:
        """从 Word 内容或文件名提取标题"""
        # 尝试从第一段提取标题（通常 Word 文档第一段是标题）
        lines = content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # 如果第一行比较短（可能是标题）
            if len(first_line) < 100 and first_line:
                return first_line
        
        # 从文件名提取
        name = Path(filename).stem
        # 移除日期后缀
        name = re.sub(r'_\d{8}$', '', name)
        return name
    
    def _extract_date(self, filename: str) -> str:
        """从文件名提取日期"""
        match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month}-{day}"
        return ""
    
    def _categorize(self, rel_path: str) -> str:
        """根据路径分类（5 大类）"""
        if '宪法' in rel_path:
            return '宪法'
        elif '法律' in rel_path:
            return '法律'
        elif '行政法规' in rel_path:
            return '行政法规'
        elif '监察' in rel_path:
            return '监察法规'
        elif '司法' in rel_path:
            return '司法解释'
        else:
            return '其他'
    
    def search(self, keyword: str, category: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """搜索文档"""
        if not keyword:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for doc in self.documents:
            # 如果指定了分类，过滤
            if category and doc['category'] != category:
                continue
            
            # 计算匹配度
            score = 0
            
            # 标题匹配（权重高）
            if keyword_lower in doc['title'].lower():
                score += 10
            
            # 内容匹配
            if keyword_lower in doc['content'].lower():
                score += 5
                # 计算出现次数
                count = doc['content'].lower().count(keyword_lower)
                score += min(count, 10)  # 最多加10分
            
            if score > 0:
                results.append({
                    **doc,
                    'score': score
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def get_by_category(self, category: str, page: int = 1, page_size: int = 100) -> Dict:
        """按分类获取文档（支持分页）"""
        results = [doc for doc in self.documents if doc['category'] == category]
        total = len(results)
        total_pages = (total + page_size - 1) // page_size
        
        # 计算分页
        start = (page - 1) * page_size
        end = start + page_size
        page_results = results[start:end]
        
        return {
            'documents': page_results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """获取单个文档"""
        for doc in self.documents:
            if doc['id'] == doc_id:
                return doc
        return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats
    
    def get_latest_documents(self, limit: int = 10) -> List[Dict]:
        """获取最新文档"""
        # 按发布日期排序
        sorted_docs = sorted(
            self.documents,
            key=lambda x: x['publish_date'] or '0000-00-00',
            reverse=True
        )
        return sorted_docs[:limit]
    
    def get_hot_documents(self, limit: int = 10) -> List[Dict]:
        """获取热门文档（按重要性排序）"""
        # 定义重要法律列表
        important_laws = [
            '民法典', '刑法', '刑事诉讼法', '民事诉讼法',
            '公司法', '劳动法', '劳动合同法', '婚姻法',
            '继承法', '物权法', '合同法', '侵权责任法',
            '行政处罚法', '行政许可法', '行政复议法',
            '证券法', '保险法', '银行法', '信托法'
        ]
        
        hot_docs = []
        for doc in self.documents:
            score = 0
            for important in important_laws:
                if important in doc['title']:
                    score += 5
            if score > 0:
                hot_docs.append({**doc, 'hot_score': score})
        
        hot_docs.sort(key=lambda x: x['hot_score'], reverse=True)
        return hot_docs[:limit]

# 全局知识库实例
knowledge_base = KnowledgeBase()
