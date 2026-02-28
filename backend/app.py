from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from docxtpl import DocxTemplate
import os
import time

app = Flask(__name__)
# 允许跨域，方便前端联调
CORS(app)


# ==========================================
# 1. 法律问题问答接口 (POST)
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    time.sleep(1)  # 模拟大模型思考延迟
    mock_reply = f"关于“{user_message}”，根据《民法典》相关规定，建议您收集相关证据。(注：此为后端模拟返回，未来在此接入腾讯元器API)"

    return jsonify({"code": 200, "data": {"reply": mock_reply}})


# ==========================================
# 2. 知识库检索接口 (GET)
# ==========================================
@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')

    time.sleep(0.5)
    mock_results = [
        {"title": f"与“{keyword}”相关的法条参考", "content": "这是模拟返回的权威法条内容..."},
        {"title": f"相关案例参考", "content": "这是模拟返回的得理数据库案例..."}
    ]

    return jsonify({"code": 200, "data": {"results": mock_results}})


# ==========================================
# 3. 法律文件识别接口 (POST)
# ==========================================
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


# ==========================================
# 4. 法律文书生成接口 (POST) - 支持通用合同与特定文书
# ==========================================
@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    doc_type = data.get('doc_type', 'complaint')

    # 映射模板文件路径
    template_map = {
        'complaint': 'templates/complaint.docx',
        'contract': 'templates/contract.docx',
        'lawyer_letter': 'templates/lawyer_letter.docx'
    }

    if doc_type not in template_map:
        return jsonify({"code": 400, "msg": "不支持的文书类型"})

    tpl_path = template_map[doc_type]

    # 安全检查：检查模板文件是否存在
    if not os.path.exists(tpl_path):
        return jsonify({"code": 500,
                        "msg": f"找不到模板文件：{tpl_path}。请确保在 backend 目录下新建了 templates 文件夹并放入了对应的 Word 模板！"})

    time.sleep(1.5)  # 模拟 AI 生成时间

    # 根据类型处理特定的数据逻辑
    if doc_type == 'complaint':
        data[
            'ai_generated_reasons'] = f"2023年某月某日，被告{data.get('defendant', '未知')}因资金周转需要向原告借款... (大模型生成内容)"
        output_name = f"{data.get('plaintiff', '未知')}_起诉状.docx"

    elif doc_type == 'contract':
        contract_name = data.get('contract_name', '通用合同')
        reqs = data.get('requirements', '无特殊要求')
        # 模拟大模型根据前端传来的核心诉求起草合同正文
        data[
            'ai_generated_clauses'] = f"【AI智能起草正文】\n第一条 核心约定\n基于甲乙双方诉求（{reqs}），现约定如下...\n\n第二条 违约责任\n若任何一方违反本合同约定，应承担赔偿责任...\n\n第三条 争议解决\n本合同履行过程中发生的争议，提交人民法院诉讼解决。"
        output_name = f"{data.get('party_a', '甲方')}_{contract_name}.docx"

    elif doc_type == 'lawyer_letter':
        data[
            'ai_generated_warning'] = f"经查，贵方擅自使用我方委托人{data.get('client', '未知')}的机密... 现要求贵方立即停止侵权。(大模型生成内容)"
        output_name = f"{data.get('client', '委托人')}_律师函.docx"

    # 使用 docxtpl 渲染模板（自动将 data 里的键值对替换 Word 里的 {{ 变量名 }}）
    doc = DocxTemplate(tpl_path)
    doc.render(data)

    # 确保保存目录存在
    if not os.path.exists('temp_docs'):
        os.makedirs('temp_docs')

    file_path = f"temp_docs/{output_name}"
    doc.save(file_path)

    # 将生成的文件返回给前端下载
    return send_file(file_path, as_attachment=True, download_name=output_name)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)