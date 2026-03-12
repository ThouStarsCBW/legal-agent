#!/usr/bin/env python3
"""
知识库管理模块 - 加载和检索法律文档 (支持 Word 文档)
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import json
from docx import Document as DocxDocument

class KnowledgeBase:
    """法律知识库"""
    
    def __init__(self, base_path: str = "E:/服务外包/法律word版"):
        self.base_path = Path(base_path)
        self.documents = []
        self.stats = {
            '宪法': 0,
            '法律': 0,
            '行政法规': 0,
            '监察法规': 0,
            '司法解释': 0
        }
        # 定义分类文件夹映射
        self.category_folders = {
            '宪法': ['宪法'],
            '法律': ['法律'],
            '行政法规': ['行政法规'],
            '监察法规': ['监察法规'],
            '司法解释': ['司法解释']
        }
        self.load_documents()
    
    def load_documents(self):
        """加载所有法律文档"""
        print("正在加载法律文档...")
        
        if not self.base_path.exists():
            print(f"警告：文档目录不存在 {self.base_path}")
            return
        
        # 遍历五个分类文件夹
        for category_name in self.category_folders.keys():
            category_path = self.base_path / category_name
            if not category_path.exists():
                print(f"警告：分类文件夹不存在 - {category_path}")
                continue
            
            print(f"\n正在加载【{category_name}】分类...")
            
            # 遍历该分类下的所有 Word 文件
            for file_path in category_path.glob('**/*.docx'):
                # 跳过临时文件
                if file_path.name.startswith('~$'):
                    continue
                    
                try:
                    # 读取 Word 文档内容
                    content = self._read_word_document(file_path)
                    if not content:
                        continue
                    
                    # 计算相对路径
                    rel_path = file_path.relative_to(self.base_path)
                    
                    # 提取标题
                    title = self._extract_title_from_word(content, file_path)
                    
                    # 提取发布日期
                    publish_date = self._extract_date_from_content(content, file_path)
                    
                    # 创建文档对象
                    doc = {
                        'id': len(self.documents),
                        'title': title,
                        'category': category_name,
                        'file_path': str(file_path),
                        'rel_path': str(rel_path),
                        'publish_date': publish_date,
                        'content': content,
                        'content_preview': content[:500] + '...' if len(content) > 500 else content
                    }
                    
                    self.documents.append(doc)
                    self.stats[category_name] += 1
                    
                except Exception as e:
                    print(f"  读取失败：{file_path} - {e}")
                    continue
        
        print(f"\n✓ 已加载 {len(self.documents)} 个法律文档")
        for cat, count in self.stats.items():
            if count > 0:
                print(f"  {cat}: {count}")
    
    def _read_word_document(self, file_path: Path) -> str:
        """读取 Word 文档内容"""
        try:
            doc = DocxDocument(file_path)
            paragraphs = []
            
            # 提取所有段落文本
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:  # 只添加非空段落
                    paragraphs.append(text)
            
            # 提取表格内容
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            row_text.append(cell_text)
                    if row_text:
                        paragraphs.append(' | '.join(row_text))
            
            return '\n'.join(paragraphs)
        except Exception as e:
            print(f"读取 Word 文档失败 {file_path}: {e}")
            return ""
    
    def _extract_title_from_word(self, content: str, file_path: Path) -> str:
        """从 Word 文档内容或文件名提取标题"""
        lines = content.strip().split('\n')
        
        # 尝试从前几行提取标题（通常是文档名称）
        for line in lines[:10]:
            line = line.strip()
            if line:
                # 移除序号、括号等前缀
                title = re.sub(r'^[\(（]?[^\)）]*[\)）]?[\s\.．:：]*', '', line)
                if title and len(title) > 5:  # 确保标题有一定长度
                    # 清理标题
                    title = title.strip(' \t\n\r.')
                    if any(c in title for c in '法条例规定办法细则'):  # 包含法律关键词
                        return title
        
        # 从文件名提取
        name = file_path.stem
        # 移除日期后缀
        name = re.sub(r'_?\d{8}$', '', name)
        name = re.sub(r'[-_]\d{4}[-_]\d{2}[-_]\d{2}$', '', name)
        return name.strip()
    
    def _extract_date_from_content(self, content: str, file_path: Path) -> str:
        """从文档内容或文件名提取发布日期"""
        lines = content.lower().split('\n')
        
        # 尝试从内容中查找发布日期
        date_patterns = [
            r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})'
        ]
        
        for line in lines[:20]:  # 只检查前 20 行
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # 年份是 4 位数
                        year, month, day = groups
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # 从文件名提取
        return self._extract_date_from_filename(file_path)
    
    def _extract_date_from_filename(self, file_path: Path) -> str:
        """从文件名提取日期"""
        filename = file_path.name
        
        # 尝试多种日期格式
        patterns = [
            r'(\d{4})[-_](\d{2})[-_](\d{2})',  # 2024-01-15 或 2024_01_15
            r'(\d{4})(\d{2})(\d{2})',  # 20240115
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return ""
    
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
                score += min(count, 10)  # 最多加 10 分
            
            if score > 0:
                results.append({
                    **doc,
                    'score': score
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def get_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """按分类获取文档"""
        results = [doc for doc in self.documents if doc['category'] == category]
        return results[:limit]
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """获取单个文档"""
        for doc in self.documents:
            if doc['id'] == doc_id:
                return doc
        return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total': len(self.documents),
            **self.stats
        }
    
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
