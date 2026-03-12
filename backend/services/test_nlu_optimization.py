"""
NLU 服务优化测试脚本
测试新增功能：
1. 直接回答指令识别
2. 追问次数限制（最多 3 次）
3. 上下文记忆
"""

from services.nlu_service import NLUService, conversation_contexts

def test_direct_answer_detection():
    """测试直接回答指令识别"""
    print("="*60)
    print("测试 1: 直接回答指令识别")
    print("="*60)
    
    nlu = NLUService()
    
    test_cases = [
        ("直接回答，别问了", True),
        ("我没有更多信息了", True),
        ("快点说怎么办", True),
        ("别问了，直接分析", True),
        ("就这些了，赶紧说", True),
        ("我想了解一下法律问题", False),
        ("房东不退押金怎么办", False),
    ]
    
    for text, expected in test_cases:
        result = nlu.check_direct_answer_intent(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入：'{text}' => {result} (期望：{expected})")
    
    print()

def test_followup_limit():
    """测试追问次数限制"""
    print("="*60)
    print("测试 2: 追问次数限制（最多 3 次）")
    print("="*60)
    
    nlu = NLUService()
    conv_id = "test_conv_001"
    
    # 模拟连续追问
    for i in range(5):
        result = nlu.analyze_user_intent(f"问题{i}", conv_id)
        followup_count = result.get('followup_count', 0)
        max_reached = result.get('max_followup_reached', False)
        
        print(f"第{i+1}次提问:")
        print(f"  - 追问计数：{followup_count}/{nlu.max_followup_rounds}")
        print(f"  - 是否完整：{result['is_complete']}")
        print(f"  - 已达到上限：{max_reached}")
        print(f"  - 直接回答请求：{result.get('direct_answer_requested', False)}")
        
        if max_reached:
            print(f"  ✓ 已达到最大追问次数，下次将强制回答")
        print()
    
    # 清理上下文
    if conv_id in conversation_contexts:
        del conversation_contexts[conv_id]

def test_context_memory():
    """测试上下文记忆"""
    print("="*60)
    print("测试 3: 上下文记忆")
    print("="*60)
    
    nlu = NLUService()
    conv_id = "test_conv_002"
    
    # 第一轮对话
    print("第一轮：用户说'房东不退押金'")
    result1 = nlu.analyze_user_intent("房东不退押金", conv_id)
    print(f"  提取要素：{result1['extracted_elements']}")
    print(f"  追问问题：{result1['followup_questions']}")
    print()
    
    # 第二轮对话（补充信息）
    print("第二轮：用户补充'押金 5000 元，在北京'")
    result2 = nlu.analyze_user_intent("押金 5000 元，在北京", conv_id)
    print(f"  提取要素：{result2['extracted_elements']}")
    print(f"  追问问题：{result2['followup_questions']}")
    print(f"  上下文中的历史要素：{conversation_contexts[conv_id]['history_elements']}")
    print()
    
    # 第三轮对话（继续补充）
    print("第三轮：用户补充'合同到期了'")
    result3 = nlu.analyze_user_intent("合同到期了", conv_id)
    print(f"  提取要素：{result3['extracted_elements']}")
    print(f"  追问问题：{result3['followup_questions']}")
    print(f"  上下文整合后的要素：{conversation_contexts[conv_id]['history_elements']}")
    print()
    
    # 检查上下文是否保留了之前的信息
    context = conversation_contexts[conv_id]
    print("✓ 上下文记忆检查:")
    print(f"  - 对话历史轮数：{len(context['conversation_history'])}")
    print(f"  - 累积要素：{list(context['history_elements'].keys())}")
    
    # 清理上下文
    if conv_id in conversation_contexts:
        del conversation_contexts[conv_id]

def test_direct_answer_command():
    """测试直接回答命令"""
    print("="*60)
    print("测试 4: 直接回答命令处理")
    print("="*60)
    
    nlu = NLUService()
    conv_id = "test_conv_003"
    
    # 先问一个问题
    print("第一轮：正常提问")
    result1 = nlu.analyze_user_intent("公司不签合同怎么办", conv_id)
    print(f"  是否完整：{result1['is_complete']}")
    print(f"  追问问题：{result1['followup_questions']}")
    print()
    
    # 用户要求直接回答
    print("第二轮：用户说'直接回答，别问了'")
    result2 = nlu.analyze_user_intent("直接回答，别问了", conv_id)
    print(f"  ✓ 直接回答请求：{result2.get('direct_answer_requested', False)}")
    print(f"  ✓ 是否完整：{result2['is_complete']}")
    print(f"  ✓ 追问问题：{result2['followup_questions']}")
    print(f"  ✓ 追问计数已重置：{result2.get('followup_count', 0)}")
    print()
    
    # 清理上下文
    if conv_id in conversation_contexts:
        del conversation_contexts[conv_id]

if __name__ == "__main__":
    print("\n开始测试 NLU 服务优化功能...\n")
    
    test_direct_answer_detection()
    test_followup_limit()
    test_context_memory()
    test_direct_answer_command()
    
    print("="*60)
    print("✓ 所有测试完成！")
    print("="*60)
