from flask import Flask, jsonify

from app.database import sqla, mongo
from app.controllers.BalanceController import balanceBlueprint
from app.controllers.TranslinkController import translinkBlueprint

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from app.helpers.AuthError import AuthError
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import auth

from rq_scheduler import Scheduler
from rq import Queue, Connection
from rq.job import Job
from worker import conn
from datetime import datetime, timedelta

from app.tools.GoSync import run
from redis import Redis

app = Flask(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=find_dotenv())

app.register_blueprint(balanceBlueprint)
app.register_blueprint(translinkBlueprint)

app.config["WTF_CSRF_ENABLED"] = True
app.secret_key = os.getenv('SECRET_KEY')


app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")
app.config["MONGODB_PORT"] = int(os.getenv("MONGODB_PORT"))
app.config["MONGODB_DB"] = os.getenv("MONGODB_DB")

app.config["REDIS_HOST"] = os.getenv("REDIS_HOST")
app.config["REDIS_PORT"] = int(os.getenv("REDIS_PORT"))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLA_URI")
app.config['STORAGE_PATH'] = os.getenv("STORAGE_PATH")


sqla.init_app(app)
mongo.init_app(app)

cred = credentials.Certificate(os.getenv('FIREBASE_CERT'))

try:
    firebase_admin.initialize_app(credential=cred)
except Exception:
    firebase_admin.get_app()

# preventing race condition
with Connection():
    q = Queue(connection=conn)
    scheduler = Scheduler(queue=q)  # rq scheduler
    # do some cron
    scheduler.cron(
        '0 */2 * * *',  # Time for first execution, in UTC timezone
        func=run,                     # Function to be queued
        # Time before the function is called again, in seconds
        queue_name='Translink-Cron',
        # Repeat this number of times (None means repeat forever)
        repeat=2
    )
    print(scheduler.get_jobs())


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
