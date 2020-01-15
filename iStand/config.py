import os

#アプリルート
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#データベース設定
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or "sqlite:///test.db"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = os.getenv('SECRET_KEY') or "secret key"

#文字化け回避
JSON_AS_ASCII = False

#各種ピン番号
PIN_MOTOR1 = 8 #時計回り用
PIN_MOTOR2 = 9 #反時計回り用
PIN_SONICSENSOR1_ECHO = 2
PIN_SONICSENSOR1_TRIG = 3
PIN_SONICSENSOR2_ECHO = 17
PIN_SONICSENSOR2_TRIG = 27

#スイッチ間
'''
PIN_SWITCHES_BETWEEN = [
    0,  # switch 1
    1,  # switch 2
    2,  # switch 3
    3   # switch 4
]
'''
PIN_SWITCHES_BOX = [
    26,  # switch 1
    13,  # switch 2
    6,   # switch 3
    5    # switch 4
]

#モーター動作周波数とデューティーサイクルの設定
MOTOR_FREQUENCY = 10000
MOTOR_DUTY = 500000
MOTOR_SPEED = 10
