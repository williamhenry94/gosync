from flask import Blueprint, current_app
from flask import render_template, url_for, request, jsonify, session, redirect
import redis as red

from datetime import datetime, timedelta
from marshmallow import ValidationError

from pymongo import MongoClient, DESCENDING
from flask_cors import cross_origin
from app.Auth import requires_auth

balanceBlueprint = Blueprint('balance', __name__)

client = MongoClient('localhost', 27017)
db = client.GoCard
gocard = db.gocard


@balanceBlueprint.route('/api/balance')
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def get_balance():
    balance = gocard.find({}).sort('data', DESCENDING)[0]
    balance = {
        'date': balance['date'],
        'price': balance['price'],
        'id': balance['id']
    }
    return jsonify(balance)


@balanceBlueprint.route('/balances')
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def get_balances():
    balances = gocard.find({}).sort('data', DESCENDING)
    balance_list = list()
    for b in balances:

        balance = {
            'date': balance['date'],
            'price': balance['price'],
            'id': balance['id']
        }
        balance_list.append(balance)

    return jsonify(balance_list)
