import json
from functools import wraps
from jose import jwt
from flask_cors import cross_origin
from six.moves.urllib.request import urlopen

from flask import Flask, jsonify, request, jsonify, _request_ctx_stack, current_app
from app.helpers.AuthError import AuthError
from firebase_admin import auth
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from app.repositories.UserRepository import get_or_create_user
# Format error response and append status code

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=find_dotenv())

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_IDENTIFIER = os.getenv('API_IDENTIFIER')
ALGORITHMS = ["RS256"]


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()

        try:
            decoded_token = auth.verify_id_token(token)
            email = decoded_token['email']
            uid = decoded_token['uid']
            user = get_or_create_user({'email': email, 'uid': uid})
            _request_ctx_stack.top.current_user = user
        except Exception as e:

            raise AuthError({"code": "invalid_header",
                             "description": str(e)}, 401)

        return f(*args, **kwargs)

    return decorated


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False
