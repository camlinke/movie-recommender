from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from rq_dashboard import RQDashboard
from rq import Queue
from redis import Redis
import os

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

redis_conn = Redis()
rq = Queue(connection=redis_conn)
RQDashboard(app)


from app import routes, models