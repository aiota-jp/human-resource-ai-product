"""環境変数の初期パスワードを使って初期ユーザーを作成する。"""
from database import init_db
from services.auth_service import ensure_default_users


if __name__ == "__main__":
    init_db()
    ensure_default_users()
    print("初期ユーザーを確認・作成しました。")
    print("パスワードは .env の *_INITIAL_PASSWORD を使用します。")
