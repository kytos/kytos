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

This endpoint creates new users:

.. code-block:: shell

    POST http://127.0.0.1:8181/api/kytos/auth/users/

    $ curl -X POST \
        -H 'Content-Type: application/json' \
        -d '{"username":"kytos",
        "password":"your_password",
        "email": "babel42@email.com"}' \
        URL

This endpoint verifies a user and returns a valid token if authentication
is correct:

.. code-block:: shell

    GET http://127.0.0.1:8181/api/kytos/auth/login/

    $ curl -X GET \
        -H 'Accept:application/json' \
        -H 'Authorization:Basic username:password' \
        URL

This endpoint lists the registered users:

.. code-block:: shell

    GET http://127.0.0.1:8181/api/kytos/auth/v1/users/

    $ curl -X GET \
        -H 'Accept:application/json' \
        -H 'Authorization: Bearer ${TOKEN}' \
        URL

This endpoint gets details about a specific user:

.. code-block:: shell

    GET http://127.0.0.1:8181/api/kytos/auth/users/<user_id>/

    $ curl -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -H 'Authorization: Bearer ${TOKEN}' \
        -d '{"user_id": "001"}' \
        URL


This endpoint deletes a specific user.

.. code-block:: shell

    DELETE http://127.0.0.1:8181/api/kytos/auth/v1/users/<user_id>/

    $ curl -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -H 'Authorization: Bearer ${TOKEN}' \
        -d '{"user_id": "001"}' \
        URL

This endpoint update a specific user:

.. code-block:: shell

    PATCH http://127.0.0.1:8181/api/kytos/auth/v1/users/<user_id>/

    $ curl -X PATCH \
        -H 'Content-Type: application/json' \
        -H 'Authorization: Bearer ${TOKEN}' \
        -d '{"user_id": "001"}' \
        URL


The process to protect an endpoint is found in session `How to protect a NApp
REST endpoint <https://docs.kytos.io/developer/creating_a_napp/>`_
.
