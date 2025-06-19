# application/utils/util.py

from datetime import datetime, timedelta, timezone
from jose import jwt
from flask import request, jsonify
from functools import wraps
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "a super secret, secret key"

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id)  # Must be a string
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.JWTError:
        return None  # Invalid token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'message': 'Token is missing'}), 401

        token = auth_header.split(" ")[1]
        user_id = decode_token(token)

        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 401

        return f(user_id, *args, **kwargs)
    return decorated
