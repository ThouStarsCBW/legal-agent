from flask import Blueprint, request, jsonify, send_file
from docxtpl import DocxTemplate
import os
from services.llm_service import generate_complaint_text, generate_contract_text

doc_bp = Blueprint('document', __name__)


# 接口 1：根据大纲，AI 撰写长文本供用户预览
@doc_bp.route('/api/generate_text', methods=['POST'])
def generate_text():
    data = request.json
    doc_type = data.get('doc_type')

    if doc_type == 'complaint':
        res_text = generate_complaint_text(
            data.get('plaintiff', ''),
            data.get('defendant', ''),
            data.get('demand', '')
        )
    elif doc_type == 'contract':
        res_text = generate_contract_text(
            data.get('contract_name', ''),
            data.get('party_a', ''),
            data.get('party_b', ''),
            data.get('requirements', '')
        )
    else:
        return jsonify({"code": 400, "msg": "不支持的文书类型"})

    return jsonify({"code": 200, "data": {"text": res_text}})


# 接口 2：接收用户最终确认的文本，填入 Word 模板并下载
@doc_bp.route('/api/export_word', methods=['POST'])
def export_word():
    data = request.json
    doc_type = data.get('doc_type')
    final_text = data.get('ai_text', '')

    template_map = {
        'complaint': 'templates/complaint.docx',
        'contract': 'templates/contract.docx'
    }

    if doc_type not in template_map:
        return jsonify({"code": 400, "msg": "不支持的类型"})

    tpl_path = template_map[doc_type]
    if not os.path.exists(tpl_path):
        return jsonify({"code": 500, "msg": f"找不到模板：{tpl_path}"})

    render_data = data.copy()
    if doc_type == 'complaint':
        render_data['ai_generated_reasons'] = final_text
        output_name = f"{data.get('plaintiff', '原告')}_起诉状.docx"
    elif doc_type == 'contract':
        render_data['ai_generated_clauses'] = final_text
        output_name = f"{data.get('party_a', '甲方')}_{data.get('contract_name', '合同')}.docx"

    doc = DocxTemplate(tpl_path)
    doc.render(render_data)

    if not os.path.exists('temp_docs'):
        os.makedirs('temp_docs')

    file_path = f"temp_docs/{output_name}"
    doc.save(file_path)

    return send_file(file_path, as_attachment=True, download_name=output_name)