******************
Auth Documentation
******************

The authentication module (kytos.core.authentication) is a resource under
development that provides a means of protection for REST endpoints.
By using this resource, endpoints that are public by default,
now require an authorization token to be accessed.

All the authentication, token generation and configuration process is handled
through the REST endpoints that are made available by default on
kytos installation:

Creating superusers
===================

To access the REST Endpoints related to Authentication, it is necessary to 
register a first user (Superuser). To do this, run kytos with the -f and -C 
arguments:

.. code-block:: shell 

   $ kytosd -f -C

   -----------------------
    username: <your_name>
    email: <your_email>
    password: <your_pass>
    re-password: <your_pass>
   


Login
=====

This endpoint verifies a user and returns a valid token if authentication
is correct:

Endpoint:

.. code-block:: shell

    GET /api/kytos/core/auth/login/

Request:

.. code-block :: shell

    curl -u username:password http://127.0.0.1:8181/api/kytos/core/auth/login/

Response:

.. code-block:: shell

    {"token": token_here}

List Users
==========

This endpoint lists the registered users:

Endpoint:

.. code-block:: shell

    GET /api/kytos/core/auth/users/

Request:

.. code-block :: shell

    curl -i http://127.0.0.1:8181/api/kytos/core/auth/users \
    -H "Authorization: Bearer token"

Response:

.. code-block:: shell

   {"users":[id]}

Get user details
================

This endpoint gets details about a specific user:

Endpoint:

.. code-block:: shell

    GET /api/kytos/core/auth/users/<user_id>/

Request:

.. code-block :: shell

    curl -i http://127.0.0.1:8181/api/kytos/core/auth/users/<user_id> \
    -H "Authorization: Bearer token"

Response:

.. code-block:: shell
 
   {"data":{"email":"user_id@email.com","username":"user_id"}}

Create extra users
==================

This endpoint allows you to create new users:

This endpoint requires a token.

Endpoint:

.. code-block:: shell

    POST /api/kytos/core/auth/users/

Request:

.. code-block :: shell

    curl -d '{"username":"<your_name>", "password":"<pass>", 
    "email": "<your_email>"}' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer token" \
    http://127.0.0.1:8181/api/kytos/core/auth/users/


Response:

.. code-block:: shell

    User successfully created

Delete a user
=============

This endpoint deletes a specific user.

Endpoint:

.. code-block:: shell

    DELETE /api/kytos/core/auth/users/<user_id>/

Request:

.. code-block :: shell

    curl -X DELETE \
    -H 'Authorization: Bearer token' \
    http://127.0.0.1:8181/api/kytos/core/auth/users/<user_id>


Response:

.. code-block :: shell

  User successfully deleted

Update a user
=============

This endpoint update a specific user:

Endpoint:

.. code-block:: shell

    PATCH /api/kytos/core/auth/users/<user_id>/

Request:

.. code-block :: shell

    curl -X PATCH \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer token' \
    -d '{"email": "teste2@gmail.com"}' \
    http://127.0.0.1:8181/api/kytos/core/auth/users/<user_id>

Response:

.. code-block :: shell

    User successfully updated

The process to protect an endpoint is found in session `How to protect a NApp
REST endpoint <https://docs.kytos.io/developer/creating_a_napp/>`_.
