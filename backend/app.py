from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.document import doc_bp
import time

app = Flask(__name__)
# 允许跨域
CORS(app)

# 注册拆分出的文书撰写蓝图接口
app.register_blueprint(doc_bp)

# ==========================================
# 保持不变的三个大功能接口
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    time.sleep(1)
    mock_reply = f"关于“{user_message}”，根据《民法典》相关规定，建议您收集相关证据。(注：此为后端模拟返回)"
    return jsonify({"code": 200, "data": {"reply": mock_reply}})

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