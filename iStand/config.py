import os

#アプリルート
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#データベース設定
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or "sqlite:///test.db"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = os.getenv('SECRET_KEY') or "secret key"

#文字化け回避
JSON_AS_ASCII = False
