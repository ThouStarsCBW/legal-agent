#!/usr/bin/env python3
"""
测试法律查询模块重构
"""
import sys
sys.path.insert(0, '.')

from knowledge_base import KnowledgeBase

def test_knowledge_base():
    """测试知识库功能"""
    print("=" * 60)
    print("开始测试法律查询模块（Word 版本）")
    print("=" * 60)
    
    # 创建知识库实例
    kb = KnowledgeBase()
    
    print("\n【统计信息】")
    stats = kb.get_stats()
    print(f"总文档数：{stats.get('total', 0)}")
    for category, count in stats.items():
        if category != 'total' and count > 0:
            print(f"  {category}: {count}")
    
    print("\n【测试搜索功能】")
    # 测试搜索
    results = kb.search("合同", limit=5)
    print(f"搜索'合同'找到 {len(results)} 个结果")
    for i, result in enumerate(results[:3], 1):
        print(f"  {i}. {result['title']} ({result['category']})")
    
    print("\n【测试分类加载】")
    for category in ['宪法', '法律', '行政法规', '监察法规', '司法解释']:
        docs = kb.get_by_category(category, limit=3)
        if docs:
            print(f"\n{category} (共{len([d for d in kb.documents if d['category']==category])}篇):")
            for doc in docs:
                print(f"  - {doc['title']}")
    
    print("\n【测试最新文档】")
    latest = kb.get_latest_documents(3)
    for doc in latest:
        print(f"  - {doc['title']} ({doc['publish_date'] or '无日期'})")
    
    print("\n【测试热门文档】")
    hot = kb.get_hot_documents(3)
    for doc in hot:
        print(f"  - {doc['title']}")
    
    print("\n✓ 所有测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_knowledge_base()
    except Exception as e:
        print(f"\n✗ 测试失败：{e}")
        import traceback
        traceback.print_exc()
