from flask import Flask, jsonify

from app.database import sqla, mongo
from app.controllers.BalanceController import balanceBlueprint
from app.controllers.TranslinkController import translinkBlueprint
# from app.controllers.RatingController import ratingBlueprint
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from app.helpers.AuthError import AuthError
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import auth

from celery import Celery
from celery.schedules import crontab
from app.celery_init import make_celery

app = Flask(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=find_dotenv())

app.register_blueprint(balanceBlueprint)
app.register_blueprint(translinkBlueprint)
# app.register_blueprint(ratingBlueprint)

app.config["WTF_CSRF_ENABLED"] = True
app.secret_key = os.getenv('SECRET_KEY')


app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")
app.config["MONGODB_PORT"] = int(os.getenv("MONGODB_PORT"))
app.config["MONGODB_DB"] = os.getenv("MONGODB_DB")

app.config["REDIS_HOST"] = os.getenv("REDIS_HOST")
app.config["REDIS_PORT"] = os.getenv("REDIS_PORT")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLA_URI")

app.config.update(
    CELERY_BROKER_URL='redis://' +
    app.config["REDIS_HOST"]+':'+app.config["REDIS_PORT"],
    CELERY_RESULT_BACKEND='redis://' +
    app.config["REDIS_HOST"]+':'+app.config["REDIS_PORT"]
)

sqla.init_app(app)
mongo.init_app(app)
celery = make_celery(app)

cred = credentials.Certificate(os.getenv('FIREBASE_CERT'))

try:
    firebase_admin.initialize_app(credential=cred)
except Exception:
    firebase_admin.get_app()


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    print('called task printer')
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )


@celery.task
def test(arg):
    print(arg)
