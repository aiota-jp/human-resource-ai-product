"""
config.py
アプリケーション設定ファイル
環境変数から設定値を読み込む
"""
import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()


class Config:
    """アプリケーション共通設定"""

    # Flask設定
    ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY")
    if ENV == "production" and not SECRET_KEY:
        raise RuntimeError("production環境ではSECRET_KEYの設定が必須です。")
    if not SECRET_KEY:
        SECRET_KEY = "dev-secret-key-please-change"

    DEBUG = ENV == "development"

    # HTTPS公開時のセッションCookie設定
    SESSION_COOKIE_SECURE = ENV == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # データベース設定
    DATABASE = os.path.join(os.path.dirname(__file__), "database.db")

    # アップロード設定
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "outputs")
    ALLOWED_EXTENSIONS = {"xlsx", "csv"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB

    # Dify設定
    DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
    DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
