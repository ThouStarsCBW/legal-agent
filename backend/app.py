from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.document import doc_bp
from services.llm_service import generate_response
from services.nlu_service import NLUService
from services.rag_service import RAGService
from services.legal_analysis_service import LegalAnalysisService
from services.action_guide_service import ActionGuideService
import time
import logging
from datetime import datetime

app = Flask(__name__)
# 允许跨域
CORS(app)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 注册拆分出的文书撰写蓝图接口
app.register_blueprint(doc_bp)

# 初始化服务
nlu_service = NLUService()
rag_service = RAGService()
legal_analysis_service = LegalAnalysisService()
action_guide_service = ActionGuideService()

# ==========================================
# 保持不变的三个大功能接口
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    logger.info("="*60)
    logger.info(f"收到新的聊天请求")
    
    data = request.json
    user_message = data.get('message', '')
    
    logger.info(f"用户消息：{user_message[:50]}...")
    
    if not user_message:
        logger.warning("消息内容为空")
        return jsonify({"code": 400, "msg": "请输入问题内容"})
    
    try:
        # 第一步：意图识别与语义理解 (NLU)
        nlu_start = time.time()
        logger.info(">> 步骤 1: 开始 NLU 意图识别...")
        nlu_result = nlu_service.analyze_user_intent(user_message)
        nlu_duration = time.time() - nlu_start
        logger.info(f"✓ NLU 完成，耗时：{nlu_duration:.2f}秒")
        
        # 如果信息不完整，返回追问问题
        if not nlu_result['is_complete']:
            followup_questions = nlu_result['followup_questions']
            logger.info(f"需要更多信息，追问问题：{followup_questions}")
            total_duration = time.time() - start_time
            logger.info(f"总耗时：{total_duration:.2f}秒")
            logger.info("="*60)
            return jsonify({
                "code": 200,
                "data": {
                    "reply": f"为了更好地帮助您，我需要了解一些详细信息：\n\n" + "\n".join([f"• {q}" for q in followup_questions]),
                    "followup_questions": followup_questions,
                    "need_more_info": True
                }
            })
        
        # 第二步：增强检索与知识对齐 (RAG)
        rag_start = time.time()
        logger.info(">> 步骤 2: 开始 RAG 知识检索...")
        legal_terminology = nlu_result['legal_terminology'].get('legal_terms', '')
        logger.info(f"法律术语：{legal_terminology[:50] if legal_terminology else '无'}...")
        rag_result = rag_service.retrieve_knowledge(user_message, legal_terminology)
        rag_duration = time.time() - rag_start
        logger.info(f"✓ RAG 完成，耗时：{rag_duration:.2f}秒")
        logger.info(f"  - 检索到法条：{len(rag_result['legal_articles'])}条")
        logger.info(f"  - 检索到案例：{len(rag_result['similar_cases'])}个")
        logger.info(f"  - 检索到司法解释：{len(rag_result['judicial_interpretations'])}个")
        
        # 第三步：逻辑推理与初步法律分析
        analysis_start = time.time()
        logger.info(">> 步骤 3: 开始法律分析...")
        legal_analysis = legal_analysis_service.perform_legal_analysis(
            user_message,
            nlu_result['extracted_elements'],
            rag_result['legal_articles'],
            rag_result['similar_cases']
        )
        analysis_duration = time.time() - analysis_start
        logger.info(f"✓ 法律分析完成，耗时：{analysis_duration:.2f}秒")
        
        # 第四步：辅助生成与行动指南
        action_start = time.time()
        logger.info(">> 步骤 4: 生成行动指南和文书...")
        action_package = action_guide_service.generate_action_package(
            user_message,
            nlu_result['extracted_elements'],
            legal_analysis,
            rag_result
        )
        action_duration = time.time() - action_start
        logger.info(f"✓ 行动指南生成完成，耗时：{action_duration:.2f}秒")
        
        # 生成最终回答
        llm_start = time.time()
        logger.info(">> 步骤 5: 调用大模型生成最终回答...")
        prompt = f"""你是一位专业且热心的中国法律顾问，服务对象是不太懂法律的普通老百姓。

用户问题：{user_message}

以下是基于 AI 分析的结果，请整合这些信息，用通俗易懂的语言回答用户：

【案情要素】
{nlu_result['extracted_elements']}

【相关法条】
{rag_result['legal_articles']}

【相似案例】
{rag_result['similar_cases']}

【权利义务分析】
{legal_analysis['rights_obligations_analysis']}

【胜诉概率评估】
{legal_analysis['win_probability_assessment']}

【诉讼时效检查】
{legal_analysis['statute_of_limitations_check']}

【维权流程指引】
{action_package['action_guide']}

请按以下结构回答：
1. 简要总结案情
2. 法律依据（引用具体法条）
3. 权利义务分析
4. 胜诉概率和风险评估
5. 时效提醒
6. 具体维权步骤
7. 如有风险，建议咨询专业律师

要求：
- 语气友善、耐心
- 用大白话解释法律概念
- 每段末尾标注法条来源
- 给出可操作的具体建议"""
        
        logger.info(f"提示词长度：{len(prompt)}字符")
        logger.info(">> 等待大模型生成完整回复...")
        response = generate_response(prompt)
        llm_duration = time.time() - llm_start
        logger.info(f"✓ 大模型回复生成完成，耗时：{llm_duration:.2f}秒")
        logger.info(f"  - 回复长度：{len(response)}字符")
        
        # 添加引用溯源
        tag_start = time.time()
        tagged_response = action_guide_service.add_source_tagging(response, rag_result)
        tag_duration = time.time() - tag_start
        logger.info(f"✓ 引用标注完成，耗时：{tag_duration:.2f}秒")
        
        total_duration = time.time() - start_time
        logger.info(f"✓ 全部完成！总耗时：{total_duration:.2f}秒")
        logger.info(f"各阶段耗时:")
        logger.info(f"  - NLU: {nlu_duration:.2f}秒")
        logger.info(f"  - RAG: {rag_duration:.2f}秒")
        logger.info(f"  - 分析：{analysis_duration:.2f}秒")
        logger.info(f"  - 文书生成：{action_duration:.2f}秒")
        logger.info(f"  - 大模型：{llm_duration:.2f}秒")
        logger.info(f"  - 引用标注：{tag_duration:.2f}秒")
        logger.info("="*60)
        
        return jsonify({
            "code": 200,
            "data": {
                "reply": tagged_response,
                "nlu_result": nlu_result,
                "rag_result": rag_result,
                "legal_analysis": legal_analysis,
                "action_package": action_package,
                "need_more_info": False
            }
        })
        
    except Exception as e:
        logger.error(f"处理请求时发生错误：{str(e)}", exc_info=True)
        total_duration = time.time() - start_time
        logger.info(f"错误发生在第{total_duration:.2f}秒")
        logger.info("="*60)
        return jsonify({"code": 500, "msg": f"AI 服务异常，请稍后重试：{str(e)}"})

@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    time.sleep(0.5)
    mock_results = [
        {"title": f"与“{keyword}”相关的法条参考", "content": "这是模拟返回的权威法条内容..."},
        {"title": f"相关案例参考", "content": "这是模拟返回的得理数据库案例..."}
    ]
    return jsonify({"code": 200, "data": {"results": mock_results}})

@app.route('/api/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "未上传文件"})
    file = request.files['file']
    time.sleep(1.5)
    return jsonify({
        "code": 200,
        "data": {
            "text": f"提取到的【{file.filename}】文本内容：\n甲方：张三\n乙方：李四...",
            "risk": "风险提示：违约金比例可能过高。"
        }
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)