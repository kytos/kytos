"""Module with main classes related to Authentication."""

# pylint: disable=invalid-name
import base64
import binascii
import datetime
import getpass
import logging
import os
import uuid
from functools import wraps
from http import HTTPStatus

import jwt
import pymongo
from pydantic import ValidationError
from pymongo.collection import ReturnDocument
from pymongo.errors import AutoReconnect, DuplicateKeyError
from pymongo.results import InsertOneResult
from tenacity import retry_if_exception_type, stop_after_attempt, wait_random

from kytos.core.config import KytosConfig
from kytos.core.db import Mongo
from kytos.core.rest_api import (HTTPException, JSONResponse, Request,
                                 content_type_json_or_415, get_json_or_400)
from kytos.core.retry import before_sleep, for_all_methods, retries
from kytos.core.user import HashSubDoc, UserDoc, UserDocUpdate

__all__ = ['authenticated']

LOG = logging.getLogger(__name__)


def authenticated(func):
    """Handle tokens from requests."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Verify the requires of token."""
        try:
            request: Request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            else:
                raise ValueError("Request arg not found in the decorated func")
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
            return JSONResponse({"error": msg},
                                status_code=HTTPStatus.UNAUTHORIZED.value)
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
                "_id": str(uuid.uuid4()),
                "username": user_data.get('username'),
                "hash": HashSubDoc(),
                "password": user_data.get('password'),
                "email": user_data.get('email'),
                "inserted_at": utc_now,
                "updated_at": utc_now,
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
        if "password" in data:
            data["hash"] = HashSubDoc()
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
        except ValidationError as err:
            msg = self.error_msg(err.errors())
            return f"Error: {msg}"
        except DuplicateKeyError:
            return f"Error: {username} already exist."

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
            "auth/users/{username}", self._list_user
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/", self._create_user, methods=["POST"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/{username}", self._delete_user, methods=["DELETE"]
        )
        self.controller.api_server.register_core_endpoint(
            "auth/users/{username}", self._update_user, methods=["PATCH"]
        )

    def _authenticate_user(self, request: Request) -> JSONResponse:
        """Authenticate a user using MongoDB."""
        if "Authorization" not in request.headers:
            raise HTTPException(400, detail="Authorization header missing")
        try:
            auth = request.headers["Authorization"]
            _scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
            username, _, password = decoded.partition(":")
            password = password.encode()
        except (ValueError, TypeError, binascii.Error) as err:
            msg = "Credentials were not correctly set."
            raise HTTPException(400, detail=msg) from err
        user = self._find_user(username)
        if user["state"] != 'active':
            raise HTTPException(401, detail='This user is not active')
        password_hashed = UserDoc.hashing(password, user["hash"])
        if user["password"] != password_hashed:
            raise HTTPException(401, detail="Incorrect password")
        time_exp = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=self.token_expiration_minutes
        )
        token = self._generate_token(username, time_exp)
        return JSONResponse({"token": token})

    def _find_user(self, username):
        """Find a specific user using MongoDB."""
        user = self.user_controller.get_user(username)
        if not user:
            raise HTTPException(404, detail=f"User {username} not found")
        return user

    @authenticated
    def _list_user(self, request: Request) -> JSONResponse:
        """List a specific user using MongoDB."""
        username = request.path_params["username"]
        user = self.user_controller.get_user_nopw(username)
        if not user:
            raise HTTPException(404, detail=f"User {username} not found")
        return JSONResponse(user)

    @authenticated
    def _list_users(self, _request: Request) -> JSONResponse:
        """List all users using MongoDB."""
        users_list = self.user_controller.get_users()
        return JSONResponse(users_list)

    @staticmethod
    def _get_request_body(request: Request) -> dict:
        """Get JSON from request"""
        content_type_json_or_415(request)
        body = get_json_or_400(request)
        if not isinstance(body, dict):
            raise HTTPException(400, "Invalid payload type: {body}")
        return body

    @staticmethod
    def error_msg(error_list: list) -> str:
        """Return a more request friendly error message from ValidationError"""
        msg = ""
        for err in error_list:
            for value in err['loc']:
                msg += value + ", "
            msg = msg[:-2]
            msg += ": " + err["msg"] + "; "
        return msg[:-2]

    @authenticated
    def _create_user(self, request: Request) -> JSONResponse:
        """Save a user using MongoDB."""
        try:
            user_data = self._get_request_body(request)
            self.user_controller.create_user(user_data)
        except ValidationError as err:
            msg = self.error_msg(err.errors())
            raise HTTPException(400, msg) from err
        except DuplicateKeyError as err:
            msg = user_data.get("username") + " already exists."
            raise HTTPException(409, detail=msg) from err
        return JSONResponse("User successfully created", status_code=201)

    @authenticated
    def _delete_user(self, request: Request) -> JSONResponse:
        """Delete a user using MongoDB."""
        username = request.path_params["username"]
        if not self.user_controller.delete_user(username):
            raise HTTPException(404, detail=f"User {username} not found")
        return JSONResponse(f"User {username} deleted succesfully")

    @authenticated
    def _update_user(self, request: Request) -> JSONResponse:
        """Update user data using MongoDB."""
        body = self._get_request_body(request)
        username = request.path_params["username"]
        allowed = ["username", "email", "password"]
        data = {}
        for key, value in body.items():
            if key in allowed:
                data[key] = value
        try:
            updated = self.user_controller.update_user(username, data)
        except ValidationError as err:
            msg = self.error_msg(err.errors())
            raise HTTPException(400, detail=msg) from err
        except DuplicateKeyError as err:
            msg = username + " already exists."
            raise HTTPException(409, detail=msg) from err
        if not updated:
            raise HTTPException(404, detail=f"User {username} not found")
        return JSONResponse("User successfully updated")
