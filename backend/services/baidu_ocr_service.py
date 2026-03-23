"""
Baidu OCR — general_basic，使用独立应用凭证（仅 OCR 使用，与语音 ASR 分离）。
环境变量：BAIDU_OCR_API_KEY、BAIDU_OCR_SECRET_KEY
Docs: https://ai.baidu.com/ai-doc/OCR/zk3h7xz52
"""
import base64
import os
import time
from typing import Dict, List, Tuple, Union

import requests
from dotenv import load_dotenv

load_dotenv()

# 专用于 OCR 的应用（百度控制台单独创建的应用）
BAIDU_OCR_API_KEY = os.getenv("BAIDU_OCR_API_KEY", "").strip()
BAIDU_OCR_SECRET_KEY = os.getenv("BAIDU_OCR_SECRET_KEY", "").strip()

TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

_ocr_token_cache: dict = {"token": None, "expires_at": 0.0}

# 简易风险提示关键词（规则，不调用大模型）
_RISK_KEYWORDS = [
    "违约金",
    "滞纳金",
    "免责",
    "最终解释权",
    "单方解除",
    "不对等",
    "霸王",
    "无限责任",
    "放弃权利",
]


def _get_ocr_access_token() -> str:
    now = time.time()
    if _ocr_token_cache["token"] and now < _ocr_token_cache["expires_at"] - 120:
        return _ocr_token_cache["token"]

    if not BAIDU_OCR_API_KEY or not BAIDU_OCR_SECRET_KEY:
        raise RuntimeError(
            "未配置 OCR 专用密钥：请在 backend/.env 中设置 BAIDU_OCR_API_KEY 与 BAIDU_OCR_SECRET_KEY"
        )

    r = requests.get(
        TOKEN_URL,
        params={
            "grant_type": "client_credentials",
            "client_id": BAIDU_OCR_API_KEY,
            "client_secret": BAIDU_OCR_SECRET_KEY,
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"Baidu OCR token 错误: {data}")
    expires_in = float(data.get("expires_in", 2592000))
    _ocr_token_cache["token"] = data["access_token"]
    _ocr_token_cache["expires_at"] = now + expires_in
    return _ocr_token_cache["token"]


def is_ocr_configured() -> bool:
    return bool(BAIDU_OCR_API_KEY and BAIDU_OCR_SECRET_KEY)


def _risk_hint(text: str) -> str:
    t = text or ""
    hits: List[str] = [w for w in _RISK_KEYWORDS if w in t]
    if not hits:
        return "未发现明显高风险关键词，仍建议由专业人士审阅全文。"
    return "风险提示：文中出现「" + "」「".join(hits) + "」等表述，请重点核对相关条款。"


def ocr_image_bytes(image_bytes: bytes) -> Tuple[bool, str]:
    """
    调用百度通用文字识别。
    返回 (ok, text_or_error_message)。
    """
    if not is_ocr_configured():
        return False, "未配置 BAIDU_OCR_API_KEY / BAIDU_OCR_SECRET_KEY（OCR 专用应用）"

    if len(image_bytes) > 4 * 1024 * 1024:
        return False, "图片过大（建议 4MB 以内）"

    try:
        token = _get_ocr_access_token()
    except Exception as e:
        return False, str(e)

    img_b64 = base64.b64encode(image_bytes).decode("ascii")
    url = f"{OCR_URL}?access_token={token}"
    r = requests.post(
        url,
        data={"image": img_b64, "language_type": "CHN_ENG"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    try:
        data = r.json()
    except Exception:
        return False, f"OCR 响应异常 HTTP {r.status_code}"

    err = data.get("error_code")
    if err is not None and err != 0:
        return False, data.get("error_msg", str(data))

    words_result = data.get("words_result") or []
    lines = []
    for item in words_result:
        if isinstance(item, dict) and "words" in item:
            lines.append(item["words"])
    text = "\n".join(lines).strip()
    if not text:
        return False, "未识别到文字，请上传清晰的含文字图片（支持 jpg/png/bmp 等）"
    return True, text


def run_ocr_upload(file_bytes: bytes, filename: str = "") -> Tuple[bool, Union[str, Dict[str, str]]]:
    """
    入口：上传文件字节。返回 (ok, err_msg) 或 (ok, {"text","risk"})。
    """
    fn = (filename or "").lower()
    if fn.endswith(".pdf"):
        return False, "当前为图片 OCR，请将 PDF 转为图片或使用截图上传。"

    ok, result = ocr_image_bytes(file_bytes)
    if not ok:
        return False, result

    return True, {"text": result, "risk": _risk_hint(result)}
