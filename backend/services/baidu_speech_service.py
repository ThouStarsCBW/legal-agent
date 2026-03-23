"""
Baidu Speech ASR (short audio) — token + server_api.
Docs: https://ai.baidu.com/ai-doc/SPEECH/Vk38lxily
"""
import base64
import os
import time
from typing import Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

BAIDU_API_KEY = os.getenv("BAIDU_API_KEY", "").strip()
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "").strip()

TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
ASR_URL = "https://vop.baidu.com/server_api"

_token_cache: dict = {"token": None, "expires_at": 0.0}


def get_baidu_access_token() -> str:
    """与语音、OCR 等百度 AI 接口共用同一 access_token 缓存。"""
    return _get_access_token()


def _get_access_token() -> str:
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 120:
        return _token_cache["token"]

    if not BAIDU_API_KEY or not BAIDU_SECRET_KEY:
        raise RuntimeError("BAIDU_API_KEY or BAIDU_SECRET_KEY not set in .env")

    r = requests.get(
        TOKEN_URL,
        params={
            "grant_type": "client_credentials",
            "client_id": BAIDU_API_KEY,
            "client_secret": BAIDU_SECRET_KEY,
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"Baidu token error: {data}")
    expires_in = float(data.get("expires_in", 2592000))
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + expires_in
    return _token_cache["token"]


def recognize_speech_wav(wav_bytes: bytes) -> Tuple[bool, str]:
    """
    Recognize speech from WAV (16kHz mono 16-bit PCM, or Baidu-supported wav).
    Returns (ok, text_or_error_message).
    """
    try:
        token = get_baidu_access_token()
    except Exception as e:
        return False, str(e)

    speech_b64 = base64.b64encode(wav_bytes).decode("ascii")
    payload = {
        "format": "wav",
        "rate": 16000,
        "channel": 1,
        "cuid": "legal-agent-web",
        "token": token,
        "speech": speech_b64,
        "len": len(wav_bytes),
        "dev_pid": 1537,
    }
    r = requests.post(ASR_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    try:
        data = r.json()
    except Exception:
        return False, f"ASR HTTP {r.status_code}: {r.text[:500]}"

    err_no = data.get("err_no")
    if err_no != 0:
        return False, data.get("err_msg", str(data))

    result = data.get("result")
    if isinstance(result, list) and result:
        text = "".join(result).strip()
        return True, text
    return False, "识别结果为空"


def is_configured() -> bool:
    return bool(BAIDU_API_KEY and BAIDU_SECRET_KEY)
