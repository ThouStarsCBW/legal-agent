from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.document import doc_bp
from services.llm_service import generate_response
from services.nlu_service import NLUService
from services.rag_service import RAGService
from services.legal_analysis_service import LegalAnalysisService
from services.action_guide_service import ActionGuideService
import time

app = Flask(__name__)
# 允许跨域
CORS(app)

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
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"code": 400, "msg": "请输入问题内容"})
    
    try:
        # 第一步：意图识别与语义理解 (NLU)
        nlu_result = nlu_service.analyze_user_intent(user_message)
        
        # 如果信息不完整，返回追问问题
        if not nlu_result['is_complete']:
            followup_questions = nlu_result['followup_questions']
            return jsonify({
                "code": 200,
                "data": {
                    "reply": f"为了更好地帮助您，我需要了解一些详细信息：\n\n" + "\n".join([f"• {q}" for q in followup_questions]),
                    "followup_questions": followup_questions,
                    "need_more_info": True
                }
            })
        
        # 第二步：增强检索与知识对齐 (RAG)
        legal_terminology = nlu_result['legal_terminology'].get('legal_terms', '')
        rag_result = rag_service.retrieve_knowledge(user_message, legal_terminology)
        
        # 第三步：逻辑推理与初步法律分析
        legal_analysis = legal_analysis_service.perform_legal_analysis(
            user_message,
            nlu_result['extracted_elements'],
            rag_result['legal_articles'],
            rag_result['similar_cases']
        )
        
        # 第四步：辅助生成与行动指南
        action_package = action_guide_service.generate_action_package(
            user_message,
            nlu_result['extracted_elements'],
            legal_analysis,
            rag_result
        )
        
        # 生成最终回答
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
        
        response = generate_response(prompt)
        
        # 添加引用溯源
        tagged_response = action_guide_service.add_source_tagging(response, rag_result)
        
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