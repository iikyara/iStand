from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('iStand.config')
config = app.config

db = SQLAlchemy(app)

from iStand.models import *

# モータデータの読み込み
config['MOTOR_FREQUENCY'] = db.session.query(Motor.frequency).first()[0]
config['MOTOR_DUTY'] = db.session.query(Motor.dutycycle).first()[0]
config['MOTOR_SPEED'] = db.session.query(Motor.speed).first()[0]

import iStand.views
import iStand.test_app
