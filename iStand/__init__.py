from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('iStand.config')

db = SQLAlchemy(app)

import iStand.views
import iStand.test_app
