from flask import Flask, jsonify

from app.database import sqla, mongo
from app.controllers.BalanceController import balanceBlueprint
from app.controllers.TranslinkController import translinkBlueprint
# from app.controllers.RatingController import ratingBlueprint
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from app.helpers.AuthError import AuthError


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

app.config['AUTH0_DOMAIN'] = os.getenv('AUTH0_DOMAIN')
app.config['API_IDENTIFIER'] = os.getenv('API_IDENTIFIER')

sqla.init_app(app)
mongo.init_app(app)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
