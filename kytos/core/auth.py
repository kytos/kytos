"""Module with main classes related to Authentication."""

# pylint: disable=invalid-name
import datetime
import getpass
import hashlib
import logging
import os
import uuid
from functools import wraps
from http import HTTPStatus

import jwt
import pymongo
from flask import jsonify, request
from pydantic import ValidationError
from pymongo.collection import ReturnDocument
from pymongo.errors import AutoReconnect, DuplicateKeyError
from pymongo.results import InsertOneResult
from tenacity import retry_if_exception_type, stop_after_attempt, wait_random
from werkzeug.exceptions import (BadRequest, Conflict, NotFound, Unauthorized,
                                 UnsupportedMediaType)

from kytos.core.config import KytosConfig
from kytos.core.db import Mongo
from kytos.core.retry import before_sleep, for_all_methods, retries
from kytos.core.user import UserDoc, UserDocUpdate

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


@for_all_methods(
    retries,
    stop=stop_after_attempt(
        int(os.environ.get("MONGO_AUTO_RETRY_STOP_AFTER_ATTEMPT", 3))
    ),
    wait=wait_random(
        min=int(os.environ.get("MONGO_AUTO_RETRY_WAIT_RANDOM_MIN", 0.1)),
        max=int(os.environ.get("MONGO_AUTO_RETRY_WAIT_RANDOM_MAX", 1)),
    ),
    before_sleep=before_sleep,
    retry=retry_if_exception_type((AutoReconnect,)),
)
class UserController:
    """UserController"""

    # pylint: disable=unnecessary-lambda
    def __init__(self, get_mongo=lambda: Mongo()):
        self.mongo = get_mongo()
        self.db_client = self.mongo.client
        self.db = self.db_client[self.mongo.db_name]

    def bootstrap_indexes(self):
        """Bootstrap all users related indexes."""
        index_tuples = [
            ("users", [("username", pymongo.ASCENDING)], {"unique": True}),
        ]
        for collection, keys, kwargs in index_tuples:
            if self.mongo.bootstrap_index(collection, keys, **kwargs):
                LOG.info(
                    f"Created DB index {keys}, collection: {collection}"
                )

    def create_user(self, user_data: dict) -> InsertOneResult:
        """Create user to database"""
        try:
            utc_now = datetime.datetime.utcnow()
            result = self.db.users.insert_one(UserDoc(**{
                **{"_id": str(uuid.uuid4())},
                **user_data,
                **{"inserted_at": utc_now},
                **{"updated_at": utc_now}
            }).dict())
        except DuplicateKeyError as err:
            raise err
        except ValidationError as err:
            raise err
        return result

    def delete_user(self, username: str) -> dict:
        """Delete user from database"""
        utc_now = datetime.datetime.utcnow()
        result = self.db.users.find_one_and_update(
            {"username": username},
            {"$set": {
                "state": "inactive",
                "deleted_at": utc_now,
            }},
            return_document=ReturnDocument.AFTER,
        )
        return result

    def update_user(self, username: str, data: dict) -> dict:
        """Update user from database"""
        utc_now = datetime.datetime.utcnow()
        try:
            result = self.db.users.find_one_and_update(
                {"username": username},
                {
                    "$set": UserDocUpdate(**{
                        **data,
                        **{"updated_at": utc_now}
                    }).dict(exclude_none=True)
                },
                return_document=ReturnDocument.AFTER
            )
        except ValidationError as err:
            raise err
        except DuplicateKeyError as err:
            raise err
        return result

    def get_user(self, username: str) -> dict:
        """Return a user information from database"""
        data = self.db.users.aggregate([
            {"$match": {"username": username}},
            {"$project": UserDoc.projection()},
            {"$limit": 1}
        ])
        try:
            user, *_ = list(value for value in data)
            return user
        except ValueError:
            return {}

    def get_user_nopw(self, username: str) -> dict:
        """Return a user information from database without password"""
        data = self.db.users.aggregate([
            {"$match": {"username": username}},
            {"$project": UserDoc.projection_nopw()},
            {"$limit": 1}
        ])
        try:
            user, *_ = list(value for value in data)
            return user
        except ValueError:
            return {}

    def get_users(self) -> dict:
        """Return all the users"""
        data = self.db.users.aggregate([
            {"$project": UserDoc.projection_nopw()}
        ])
        return {'users': list(value for value in data)}


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
        """Create a superuser using MongoDB."""
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
        user = {
            "username": username,
            "email": email,
            "password": password,
        }
        try:
            self.user_controller.create_user(user)
        except ValidationError:
            print("Inputs could not be validated.")
        except DuplicateKeyError:
            print(f"{username} already exist.")

        return "User successfully created"

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
            "auth/users/", self._list_users,
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
        """Authenticate a user using MongoDB."""
        username = request.authorization["username"]
        password = request.authorization["password"].encode()
        try:
            user = self._find_user(username)
            if user["password"] != hashlib.sha512(password).hexdigest():
                raise Unauthorized
            time_exp = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=self.token_expiration_minutes
            )
            token = self._generate_token(username, time_exp)
            return {"token": token}, HTTPStatus.OK.value
        except Unauthorized:
            result = "Incorrect password"
            return result, HTTPStatus.UNAUTHORIZED.value

    def _find_user(self, username):
        """Find a specific user using MongoDB."""
        user = self.user_controller.get_user(username)
        if not user:
            result = f"User {username} not found"
            raise NotFound(result)
        return user

    @authenticated
    def _list_user(self, username):
        """List a specific user using MongoDB."""
        user = self.user_controller.get_user_nopw(username)
        if not user:
            result = f"User {username} not found"
            raise NotFound(result)
        return user

    @authenticated
    def _list_users(self):
        """List all users using MongoDB."""
        users_list = self.user_controller.get_users()
        return users_list

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
        """Save a user using MongoDB."""
        try:
            self.user_controller.create_user(self._get_request())
        except ValidationError as err:
            raise BadRequest from err
        except DuplicateKeyError as err:
            raise Conflict from err
        return jsonify("User successfully created"), 201

    @authenticated
    def _delete_user(self, username):
        """Delete a user using MongoDB."""
        if not self.user_controller.delete_user(username):
            raise NotFound(f"User {username} not found")
        return jsonify(f"User {username} deleted succesfully"), 200

    @authenticated
    def _update_user(self, username):
        """Update user data using MongoDB."""
        req = self._get_request()
        allowed = ["username", "email", "password"]
        data = {}
        for key, value in req.items():
            if key in allowed:
                data[key] = value
        try:
            updated = self.user_controller.update_user(username, data)
        except ValidationError as err:
            raise BadRequest from err
        except DuplicateKeyError as err:
            raise Conflict from err
        if not updated:
            raise NotFound(f"User {username} not found")
        return jsonify("User successfully updated"), 200
