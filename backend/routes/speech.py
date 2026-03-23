from flask import Blueprint, request, jsonify

from services.baidu_speech_service import recognize_speech_wav, is_configured

speech_bp = Blueprint("speech", __name__)


@speech_bp.route("/api/speech/asr", methods=["POST"])
def speech_asr():
    if not is_configured():
        return jsonify(
            {
                "code": 503,
                "msg": "未配置百度语音：请在 backend/.env 中设置 BAIDU_API_KEY 与 BAIDU_SECRET_KEY",
            }
        )

    if "audio" not in request.files:
        return jsonify({"code": 400, "msg": "未上传音频文件 audio"})

    f = request.files["audio"]
    raw = f.read()
    if not raw:
        return jsonify({"code": 400, "msg": "音频为空"})

    ok, text = recognize_speech_wav(raw)
    if not ok:
        return jsonify({"code": 500, "msg": text})

    return jsonify({"code": 200, "data": {"text": text}})
