"""Module with main classes related to Authentication."""

# pylint: disable=invalid-name
import datetime
import getpass
import hashlib
import logging
import time
from functools import wraps
from http import HTTPStatus

import jwt
import pymongo
from flask import jsonify, request
from pymongo.collection import ReturnDocument
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from kytos.core.config import KytosConfig
from kytos.core.db import Mongo
from kytos.core.events import KytosEvent
from kytos.core.user import UserDoc

__all__ = ['authenticated']

LOG = logging.getLogger(__name__)


def authenticated(func):
    """Handle tokens from requests."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Verify the requires of token."""
        try:
            content = request.headers.get("Authorization")
            if content is None:
                raise ValueError("The attribute 'content' has an invalid "
                                 "value 'None'.")
            token = content.split("Bearer ")[1]
            jwt.decode(token, key=Auth.get_jwt_secret(),
                       algorithms=[Auth.encode_algorithm])
        except (
            ValueError,
            IndexError,
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.DecodeError,
        ) as exc:
            msg = f"Token not sent or expired: {exc}"
            return jsonify({"error": msg}), HTTPStatus.UNAUTHORIZED.value
        return func(*args, **kwargs)

    return wrapper


class UserController:
    """UserController"""

    # pylint: disable=unnecessary-lambda
    def __init__(self, get_mongo=lambda: Mongo()):
        self.mongo = get_mongo()
        self.db_client = self.mongo.client
        self.db = self.db_client[self.mongo.db_name]

    def bootstrap_indexes(self):
        """Bootstrap all topology related indexes."""
        index_tuples = [
            ("users", [("username", pymongo.ASCENDING)]),
        ]
        for collection, keys in index_tuples:
            if self.mongo.bootstrap_index(collection, keys):
                LOG.info(
                    f"Created DB index {keys}, collection: {collection})"
                )

    def create_user(self, user_data):
        """Create user to database"""
        utc_now = datetime.datetime.utcnow()
        data = {
            "username": user_data["username"],
            "email": user_data["email"],
            "password": user_data["password"],
            "inserted_at": utc_now,
            "updated_at": utc_now,
        }
        try:
            user = UserDoc(**data)
        except ValueError as error:
            raise error
        result = self.db.users.insert_one(user.dict())
        return result

    def delete_user(self, username):
        """Delete user from database"""
        utc_now = datetime.datetime.utcnow()
        update = {
                "state": "inactive",
                "deleted_at": utc_now,
        }
        result = self.db.users.find_one_and_update(
            {"username": username},
            {"$set": update},
            return_document=ReturnDocument.AFTER,
        )
        return result

    def update_user(self, username, data):
        """Update user from database"""
        data.update({"updated_at": datetime.datetime.utcnow()})
        result = self.db.users.find_one_and_update(
            {"username": username},
            data
        )
        return result

    def get_user(self, username):
        """Return a user information from database"""
        data = self.db.users.aggregate([
            {"$match": {"username": username}},
            {"$project": UserDoc.projection()}
        ])
        return {"users": {value["username"]: value for value in data}}

    def get_users(self):
        """Return all the users"""
        data = self.db.users.aggregate([
            {"$project": UserDoc.projection()}
        ])
        return {"users": {value["username"]: value for value in data}}


class Auth:
    """Module used to provide Kytos authentication routes."""

    encode_algorithm = "HS256"

    def __init__(self, controller):
        """Init method of Auth class takes the parameters below.

        Args:
            controller(kytos.core.controller): A Controller instance.

        """
        self.user_controller = self.get_user_controller()
        self.user_controller.bootstrap_indexes()
        self.controller = controller
        self.namespace = "kytos.core.auth.users"
        self.token_expiration_minutes = self.get_token_expiration()
        if self.controller.options.create_superuser is True:
            self._create_superuser()

    @staticmethod
    def get_user_controller():
        """Get UserController"""
        return UserController()

    @staticmethod
    def get_token_expiration():
        """Return token expiration time in minutes defined in kytos conf."""
        options = KytosConfig().options['daemon']
        return options.token_expiration_minutes

    @classmethod
    def get_jwt_secret(cls):
        """Return JWT secret defined in kytos conf."""
        options = KytosConfig().options['daemon']
        return options.jwt_secret

    @classmethod
    def _generate_token(cls, username, time_exp):
        """Generate a jwt token."""
        return jwt.encode(
            {
                'username': username,
                'iss': "Kytos NApps Server",
                'exp': time_exp,
            },
            Auth.get_jwt_secret(),
            algorithm=cls.encode_algorithm,
        )

    def _create_superuser(self):
        """Create a superuser using Storehouse."""
        def _create_superuser_callback(_event, box, error):
            if error:
                LOG.error('Superuser was not created. Error: %s', error)
            if box:
                LOG.info("Superuser successfully created")

        def get_username():
            return input("Username: ")

        def get_email():
            return input("Email: ")

        username = get_username()
        email = get_email()

        while True:
            password = getpass.getpass()
            re_password = getpass.getpass('Retype password: ')
            if password == re_password:
                break
            print('Passwords do not match. Try again')

        user = {
            "username": username,
            "email": email,
            "password": hashlib.sha512(password.encode()).hexdigest(),
        }
        content = {
            "namespace": self.namespace,
            "box_id": user["username"],
            "data": user,
            "callback": _create_superuser_callback,
        }
        event = KytosEvent(name="kytos.storehouse.create", content=content)
        self.controller.buffers.app.put(event)
        user["password"] = password
        self.user_controller.create_user(user)

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
            "auth/users/<username>", self._list_user
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/", self._create_user, methods=["POST"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/<username>", self._delete_user, methods=["DELETE"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/<username>", self._update_user, methods=["PATCH"]
        )

    def _authenticate_user(self):
        """Authenticate a user using Storehouse."""
        username = request.authorization["username"]
        password = request.authorization["password"].encode()
        try:
            user = self._find_user(username)[0].get("data")
            if user.get("password") != hashlib.sha512(password).hexdigest():
                raise KeyError
            time_exp = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=self.token_expiration_minutes
            )
            token = self._generate_token(username, time_exp)
            return {"token": token}, HTTPStatus.OK.value
        except (AttributeError, KeyError) as exc:
            result = f"Incorrect username or password: {exc}"
            return result, HTTPStatus.UNAUTHORIZED.value

    def _find_user(self, uid):
        """Find a specific user using Storehouse."""
        response = {}

        def _find_user_callback(_event, box, error):
            nonlocal response
            if not box:
                response = {
                    "answer": f'User with uid {uid} not found',
                    "code": HTTPStatus.NOT_FOUND.value
                }
            elif error:
                response = {
                    "answer": "User data cannot be shown",
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                }
            else:
                response = {
                    "answer": {"data": box.data},
                    "code": HTTPStatus.OK.value,
                }

        content = {
            "box_id": uid,
            "namespace": self.namespace,
            "callback": _find_user_callback,
        }
        event = KytosEvent(name="kytos.storehouse.retrieve", content=content)
        self.controller.buffers.app.put(event)
        while True:
            time.sleep(0.1)
            if response:
                break
        return response["answer"], response["code"]

    @authenticated
    def _list_user(self, username):
        """List a specific user using Storehouse."""
        answer = self.user_controller.get_user(username)
        return answer

    @authenticated
    def _list_users(self):
        """List all users using Storehouse."""
        answer = self.user_controller.get_users()
        return answer

    @staticmethod
    def _get_request():
        """Get JSON from request"""
        try:
            metadata = request.json
            content_type = request.content_type
        except BadRequest as err:
            result = 'The request body is not a well-formed JSON.'
            raise BadRequest(result) from err
        if content_type is None:
            result = 'The request body is empty.'
            raise BadRequest(result)
        if metadata is None:
            if content_type != 'application/json':
                result = ('The content type must be application/json '
                          f'(received {content_type}).')
            else:
                result = 'Metadata is empty.'
            raise UnsupportedMediaType(result)
        return metadata

    @authenticated
    def _create_user(self):
        """Save a user using Storehouse."""
        req = self._get_request()
        try:
            data = {
                "username": req["username"],
                "email": req["email"],
                "password": req["password"],
            }
        except KeyError as error:
            return jsonify(f"{error} is not found in request"), 404

        self.user_controller.create_user(data)
        return jsonify("User successfully created"), 200

    @authenticated
    def _delete_user(self, username):
        """Delete a user using Storehouse."""
        if self.user_controller.delete_user(username) is None:
            return jsonify(f"User {username} not found"), 404
        return jsonify(f"User {username} deleted succesfully"), 200

    @authenticated
    def _update_user(self, username):
        """Update user data using Storehouse."""
        req = self._get_request()
        allowed = ["username", "email", "password"]
        data = {}
        for key, value in req.items():
            if key in allowed:
                data[key] = value
        self.user_controller.update_user(username, data)
        return jsonify("User successfully updated"), 200
