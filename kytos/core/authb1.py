from functools import wraps

import jwt

# Third-party imports
from flask import request, jsonify

__all__ = ['Authenticated']

JWT_SECRET = 'secret'


def Authenticated(func):
    """Handle tokens from requests."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Verify the requires of token."""
        try:
            content = request.headers.get('Authorization')
            if content is None:
                msg = 'Token not sent or expired.'
                return jsonify({'error': msg}), 401
            else:
                token = content.split("Bearer")[1]
                print(token)
            token_data = jwt.decode(token, key=JWT_SECRET)
            print("token data " + token_data)
        except Exception as erro:
            msg = 'Token not sent or expired.'
            print("erro: ", erro)
            return jsonify({'error': msg}), 401
        return func(*args, **kwargs)

    return wrapper
