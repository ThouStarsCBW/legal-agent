import os
import re
import sqlite3
import secrets
import time
from typing import Optional, Tuple, Union

from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    c = _conn()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at REAL NOT NULL
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )"""
    )
    c.commit()
    c.close()


def register_user(username: str, password: str) -> Tuple[bool, str]:
    u = (username or "").strip()
    if not re.match(r"^[a-zA-Z0-9_]{3,50}$", u):
        return False, "用户名为 3～50 位字母、数字或下划线"
    if len(password) < 6:
        return False, "密码至少 6 位"
    ph = generate_password_hash(password)
    c = _conn()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?,?,?)",
            (u, ph, time.time()),
        )
        c.commit()
    except sqlite3.IntegrityError:
        c.close()
        return False, "用户名已存在"
    c.close()
    return True, ""


def _create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    exp = time.time() + 7 * 86400
    c = _conn()
    c.execute(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)",
        (token, user_id, exp),
    )
    c.commit()
    c.close()
    return token


def login_user(username: str, password: str) -> Tuple[bool, Optional[str], str]:
    u = (username or "").strip()
    c = _conn()
    row = c.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (u,)
    ).fetchone()
    c.close()
    if not row:
        return False, None, "用户名或密码错误"
    uid, ph = row
    if not check_password_hash(ph, password):
        return False, None, "用户名或密码错误"
    token = _create_session(uid)
    return True, token, ""


def validate_token(token: str) -> Tuple[bool, Union[dict, str]]:
    if not token or len(token) < 8:
        return False, "无效令牌"
    c = _conn()
    row = c.execute(
        """SELECT s.user_id, s.expires_at, u.username
           FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token = ?""",
        (token,),
    ).fetchone()
    c.close()
    if not row:
        return False, "会话已失效，请重新登录"
    uid, exp, username = row
    if time.time() > exp:
        return False, "登录已过期，请重新登录"
    return True, {"id": uid, "username": username}


def logout_token(token: str) -> None:
    if not token:
        return
    c = _conn()
    c.execute("DELETE FROM sessions WHERE token = ?", (token,))
    c.commit()
    c.close()
