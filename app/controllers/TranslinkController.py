from flask import Blueprint, current_app
from flask import render_template, url_for, request, jsonify, session, redirect

import redis as red

from app.database import sqla
from datetime import datetime, timedelta
from marshmallow import ValidationError
from app.models.Translink import Translink
from app.repositories.TranslinkRepository import store, delete, get_account, edit
from app.forms.TranslinkForm import TranslinkForm

from pymongo import MongoClient, DESCENDING

translinkBlueprint = Blueprint('translink', __name__)


@translinkBlueprint.route('/api/translink', methods=['POST'])
def store_translink_account():
    req = request.get_json()
    if req == None:
        return jsonify({'message': 'Invalid Request'}), 400

    schema = TranslinkForm()
    try:
        validation = schema.load(req)
        data = store(schema.dump(req))

        return jsonify(
            {
                "id": data.id,
                "gocard_number": data.gocard_number
            }
        ), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@translinkBlueprint.route('/api/translink/<int:id>', methods=['PUT'])
def edit_translink_account(id):
    req = request.get_json()
    if req == None:
        return jsonify({'message': 'Invalid Request'}), 400

    schema = TranslinkForm()
    try:
        validation = schema.load(req)
        data = edit(id, schema.dump(req))

        if data:
            return jsonify(
                {
                    "message": "Gocard detail updated"
                }
            )
        else:
            return jsonify(
                {
                    "message": "Gocard detail cannot be updated"
                }
            ), 410

    except ValidationError as err:
        return jsonify(err.messages), 400


@translinkBlueprint.route('/api/translink/<int:id>')
def get_translink_account(id):
    account = get_account(id)
    if account:
        return jsonify(account)
    else:
        return jsonify({'message': 'Account not found'}), 404


@translinkBlueprint.route('/api/translink/<int:id>', methods=['DELETE'])
def delete_translink_account(id):

    status = delete(id)
    if status:
        return jsonify({
            'message': 'Account removed'
        }), 201
    else:
        return jsonify({
            'message': 'Account cannot be deleted'
        }), 410
