"""ログイン認証・ロール認可サービス"""
import os
from functools import wraps

from flask import session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


INITIAL_USERS = (
    ("admin", "ADMIN_INITIAL_PASSWORD", "admin"),
    ("staff", "STAFF_INITIAL_PASSWORD", "staff"),
    ("user", "USER_INITIAL_PASSWORD", "user"),
    ("EMP001", "EMP001_INITIAL_PASSWORD", "user"),
)


def get_default_users() -> tuple[tuple[str, str, str], ...]:
    """初期ユーザーのパスワードを環境変数から取得する。"""
    users = []
    missing = []

    for username, env_name, role in INITIAL_USERS:
        password = os.environ.get(env_name, "").strip()
        if not password:
            missing.append(env_name)
        users.append((username, password, role))

    if missing:
        raise RuntimeError(
            "初期パスワードの環境変数が未設定です: " + ", ".join(missing)
        )

    return tuple(users)


def ensure_default_users() -> None:
    """初期ユーザーを作成する。既存ユーザーは変更しない。"""
    conn = get_db()
    try:
        for username, password, role in get_default_users():
            exists = conn.execute(
                "SELECT id FROM user WHERE username = ?", (username,)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), role),
                )
        conn.commit()
    finally:
        conn.close()


def ensure_default_admin() -> None:
    """後方互換用。初期ユーザーを作成する。"""
    ensure_default_users()


def authenticate(username: str, password: str) -> dict | None:
    conn = get_db()
    user = conn.execute(
        """
        SELECT u.*, e.id AS employee_id, e.name AS employee_name
          FROM user u
          LEFT JOIN employee e
                 ON e.employee_no = u.username AND e.is_active = 1
         WHERE u.username = ?
        """,
        (username,),
    ).fetchone()
    conn.close()
    if user and check_password_hash(user["password"], password):
        return dict(user)
    return None


def login_required(view_func):
    """ログイン済みユーザーだけアクセスを許可する。"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("ログインしてください", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def roles_required(*allowed_roles):
    """指定したロールだけアクセスを許可する。"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                flash("ログインしてください", "warning")
                return redirect(url_for("login"))

            if session.get("role") not in allowed_roles:
                flash("この機能を利用する権限がありません", "danger")
                return redirect(url_for("index"))

            return view_func(*args, **kwargs)
        return wrapper
    return decorator
