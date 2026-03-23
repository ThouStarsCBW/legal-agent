from flask import Blueprint, g, jsonify, request

from services.auth_service import login_user, logout_token, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    ok, msg = register_user(username, password)
    if not ok:
        return jsonify({"code": 400, "msg": msg})
    return jsonify({"code": 200, "msg": "注册成功"})


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    ok, token, err = login_user(username, password)
    if not ok:
        return jsonify({"code": 401, "msg": err or "登录失败"})
    return jsonify(
        {
            "code": 200,
            "data": {"token": token, "username": (username or "").strip()},
        }
    )


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else ""
    logout_token(token)
    return jsonify({"code": 200, "msg": "ok"})


@auth_bp.route("/api/auth/me", methods=["GET"])
def me():
    return jsonify({"code": 200, "data": {"username": g.user["username"]}})
