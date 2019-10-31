"""Module with main classes related to Authentication."""
import datetime
import hashlib
import logging
import time
from functools import wraps
from http import HTTPStatus

import jwt
from flask import jsonify, request

from kytos.core.events import KytosEvent

__all__ = ['authenticated']

LOG = logging.getLogger(__name__)
JWT_SECRET = "secret"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "youshallnotpass"
DEFAULT_EMAIL = "admin@kytos.io"


def authenticated(func):
    """Handle tokens from requests."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Verify the requires of token."""
        try:
            content = request.headers.get("Authorization")
            if content is None:
                raise AttributeError
            token = content.split("Bearer ")[1]
            jwt.decode(token, key=JWT_SECRET)
        except (
            AttributeError,
            jwt.ExpiredSignature,
            jwt.exceptions.DecodeError,
        ):
            msg = "Token not sent or expired."
            return jsonify({"error": msg}), 401
        return func(*args, **kwargs)

    return wrapper


class Auth:
    """Module used to provide Kytos authentication routes."""

    def __init__(self, controller):
        """Init method of Auth class takes the parameters below.

        Args:
            controller(kytos.core.controller): A Controller instance.

        """
        self.controller = controller
        self.namespace = "kytos.core.auth.users"
        self._create_default_user()

    @classmethod
    def _generate_token(cls, username, time_exp):
        """Generate a jwt token."""
        return jwt.encode(
            {
                'username': username,
                'iss': "Kytos NApps Server",
                'exp': time_exp,
            },
            JWT_SECRET,
            algorithm='HS256',
        )

    def _create_default_user(self):
        """Create a default user using Storehouse."""
        def _create_default_user_callback(_event, box, error):
            if box and not error:
                LOG.info("Default user successfully created")

        user = {
            "username": DEFAULT_USERNAME,
            "email": DEFAULT_EMAIL,
            "password": hashlib.sha512(DEFAULT_PASSWORD.encode()).hexdigest(),
        }
        content = {
            "namespace": self.namespace,
            "box_id": user["username"],
            "data": user,
            "callback": _create_default_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.create", content=content)
        self.controller.buffers.app.put(event)

    def register_core_auth_services(self):
        """
        Register /kytos/core/ services over authentication.

        It registers create, authenticate, list all, list specific, delete and
        update users.
        """
        self.controller.api_server.register_core_endpoint(
            "auth/login/", self._authenticate_user
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/", self._list_users
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/<uid>", self._list_user
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/", self._create_user, methods=["POST"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/<uid>", self._delete_user, methods=["DELETE"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/<uid>", self._update_user, methods=["PATCH"]
        )

    def _authenticate_user(self):
        """Authenticate a user using Storehouse."""
        username = request.authorization["username"]
        password = request.authorization["password"].encode()
        try:
            user = self._list_user(username)[0].get("data")
            if user.get("password") != hashlib.sha512(password).hexdigest():
                raise
            time_exp = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=10
            )
            token = self._generate_token(username, time_exp)
            return {"token": token.decode()}, HTTPStatus.OK.value
        except KeyError:
            result = "Incorrect username or password"
            return result, HTTPStatus.UNAUTHORIZED.value

    def _list_users(self):
        """List all users using Storehouse."""
        response = {}

        def _list_users_callback(_event, boxes, error):
            nonlocal response
            if error:
                response = {
                    "answer": "Users cannot be listed",
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                }
            else:
                response = {
                    "answer": {"users": boxes},
                    "code": HTTPStatus.OK.value,
                }

        content = {
            "namespace": self.namespace,
            "callback": _list_users_callback,
        }
        event = KytosEvent(name="kytos.storehouse.list", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]

    def _list_user(self, uid):
        """List a specific user using Storehouse."""
        response = {}

        def _list_user_callback(_event, box, error):
            nonlocal response
            if error or not box:
                response = {
                    "answer": "User data cannot be shown",
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                }
            else:
                # del box.data['password']
                response = {
                    "answer": {"data": box.data},
                    "code": HTTPStatus.OK.value,
                }

        content = {
            "box_id": uid,
            "namespace": self.namespace,
            "callback": _list_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.retrieve", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]

    @authenticated
    def _create_user(self):
        """Save a user using Storehouse."""
        response = {}

        def _create_user_callback(_event, box, error):
            nonlocal response
            if error or not box:
                response = {
                    "answer": "User cannot be created",
                    "code": HTTPStatus.CONFLICT.value,
                }
            else:
                response = {
                    "answer": "User successfully created",
                    "code": HTTPStatus.OK.value,
                }

        req = request.json
        password = req["password"].encode()
        data = {
            "username": req["username"],
            "email": req["email"],
            "password": hashlib.sha512(password).hexdigest(),
        }
        content = {
            "namespace": self.namespace,
            "box_id": data["username"],
            "data": data,
            "callback": _create_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.create", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]

    @authenticated
    def _delete_user(self, uid):
        """Delete a user using Storehouse."""
        response = {}

        def _delete_user_callback(_event, box, error):
            nonlocal response
            if error or not box:
                response = {
                    "answer": "User has not been deleted",
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                }
            else:
                response = {
                    "answer": "User successfully deleted",
                    "code": HTTPStatus.OK.value,
                }

        content = {
            "box_id": uid,
            "namespace": self.namespace,
            "callback": _delete_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.delete", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]

    @authenticated
    def _update_user(self, uid):
        """Update user data using Storehouse."""
        response = {}

        def _update_user_callback(_event, box, error):
            nonlocal response
            if error or not box:
                response = {
                    "answer": "User has not been updated",
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                }
            else:
                response = {
                    "answer": "User successfully updated",
                    "code": HTTPStatus.OK.value,
                }

        req = request.json
        allowed = ["username", "email", "password"]

        data = {}
        for key, value in req.items():
            if key in allowed:
                data[key] = value

        content = {
            "namespace": self.namespace,
            "box_id": uid,
            "data": data,
            "callback": _update_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.update", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]
