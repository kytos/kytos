************************
How to develop your NApp
************************

To create your own NApp you will need to use the `kytos` command provider by
`kytos-utils` package. This package is already installed in your system if you
setup your develop environment.

To see the `kytos` helper you must run the following command to display the
helper in the command line.

.. code-block:: shell

  (kytos-environment)$ kytos -h
  kytos - The kytos command line.

  Usage: kytos [-c <file>|--config <file>] <command> [<args>...]
         kytos [-v|--version]
         kytos [-h|--help]

  Options:
    -c <file>, --config <file>    Load config file [default: ~/.kytosrc]
    -h, --help                    Show this screen.
    -v, --version                 Show version.

  The most commonly used kytos commands are:
     napps      Create, list, enable, install (and other actions) NApps.
     server     Start, Stop your Kytos Controller (Kytos)
     web        Manage the Web User Interface

  See 'kytos <command> -h|--help' for more information on a specific command.


In this section we will use the command `kytos napps` to handle your own NApp.

Create your NApp
================

To create your NApp you need to use your napp-server name and insert some NApp
information. Using the following command you will create a basic structure.


.. code-block:: shell

  (kytos-environment)$ kytos napps create
  --------------------------------------------------------------
  Welcome to the bootstrap process of your NApp.
  --------------------------------------------------------------
  In order to answer both the username and the napp name,
  You must follow this naming rules:
  - name starts with a letter
  - name contains only letters, numbers or underscores
  - at least three characters
  --------------------------------------------------------------

  Please, insert your NApps Server username: <username>
  Please, insert your NApp name: <napp name>
  Please, insert a brief description for your NApp [optional]: <brief description>

  Congratulations! Your NApp have been bootstrapped!
  Now you can go to the directory tutorial/helloworld and begin to code your NApp.
  Have fun!

After that a folder with `username` will be created and inside that we have
your NApp folder.

Understanding the NApp structure
--------------------------------

After created your NApp we have the basic NApp structure.

.. code-block:: shell

   <username>/
   ├── __init__.py
   └── <napp_name>/
       ├── __init__.py
       ├── kytos.json
       ├── main.py
       ├── README.rst
       ├── settings.py
       └── ui/
           ├── k-action-menu
           ├── k-info-panel
           ├── k-toolbar
           └── README.rst


- **kytos.json**: This file contains your NApp’s metadata.
- **settings.py**: Main settings parameters of your NApp.
- **main.py**: Main source code of your NApp.
- **README.rst**: Main description and information about your NApp.
- **ui**: Folder with components to be displayed in the Kytos UI
- **ui/README.rst**: A file with a brief description of your NApp components.


How to create a rest endpoint for your napp
===========================================

In the Kytos Project we have a decorator to create new API endpoints.
If you want to create a new endpoint you should follow the steps below.

- You need import the rest decorator method.
- You need  declare a function using the rest decorator
- In the end of function you need return a string and the status code of your method.

.. code-block:: python

  from flask import jsonify # import jsonify method to convert json to string

  from kytos.core.napps import rest #import rest decorator method

  class Main(KytosNapps): # KytosNapps class

    # all KytosNapps methods

    # call the rest decorator to register your endpoint
    @rest('sample_endpoint/<name>', methods=['GET'])
    def my_endpoint(self, name):
     """Sample of documentation.

     Description for your method.
     """
     result = {"name": name}
     return jsonify(result), 200 # return a string and http status code

When the kytos starts this napp will register an endpoint called
`/api/<username>/<napp_name>/sample_endpoint/<name>` handling only **GET**
methods.

If you try open your browser using this endpoint, you will always get in the
browser the result below, where `name` was given in the browser.

.. code-block:: json

  {
    "name": "<name>"
  }


How to document your API Rest
=============================

If your NApp have to use the decorator `rest` to create some API endpoint you
need to document this endpoint. In the `kytos-utils` package there is a
command to create a basic **openapi.yml** structure to document your API.

To create the openapi file just run the follow command.

.. code-block:: shell

  (kytos-environment)$ kytos napps prepare
  Do you have REST endpoints and wish to create an API skeleton in openapi.yml? (Y/n)
  Please, update your openapi.yml file.


After that a new file called openapi.yml will be created and you can update
that to display your API documentation. To learn more how to  fill the
documentation you can see the `OpenAPI Specification <https://swagger.io/specification/>`__


An example of openapi.yml using the main.py edited in the previous section is
displayed below.

.. code-block:: yaml

    openapi: 3.0.0
    info:
      title: macartur/tutorial
      version: latest
      description: # TODO: <<<< Insert your NApp description here >>>>
    paths:
      /api/macartur/tutorial/sample_endpoint/{name}:
        get:
          summary: Sample of documentation
          description: Description of your method
          parameters:  # If you have parameters in the URL
            - name: Parameter's name as in path.
              required: true
              description: Describe parameter here
              in: path
          responses:
            200:  # You can add more responses
              description: Describe a successful call.
              content:
                application/json:  # You can also use text/plain, for example
                  schema:
                    type: object  # Adapt to your response
                    properties:
                      prop_one:
                        type: string
                        description: Meaning of prop_one
                        example: an example of prop_one
                      second_prop:
                        type: integer
                        description: Meaning of second_prop
                        example: 42

How to register yourself in the NApps respository
=================================================

To publish your NApp in the `Napps server <https://napps.kytos.io/>`_ you need
to self register.Tto do that the tool `kytos` has a command
line to make the registration. Below we have the steps to make the
registration.

First of all use the command below and pass the your user information.

.. code-block:: shell

  (kytos-environment)$ kytos users register
  --------------------------------------------------------------
  Welcome to the user registration process.
  --------------------------------------------------------------
  To continue you must fill the following fields.
  Insert the field using the pattern below:
    - start with letter
    - insert only numbers and letters
  Username (Required): <username>
  Insert the field using the pattern below:
    - insert only letters
  First Name (Required): <first name>
  Insert the field using the pattern below:
    - insert only letters
  Last Name: <last name>
  Insert the field using the pattern below:
    - insert only the caracters: [letters, numbers, _, %, &, -, $]
    - must be at least 6 characters
  Password (Required): <password>
  Confirm your password: <password confirmation>
  Insert the field using the pattern below:
    - follow the format: <login>@<domain>
      e.g. john@test.com
  Email (Required): <email>
  Insert the field using the pattern below:
    - insert only numbers
  Phone: <phone>
  Insert the field using the pattern below:
    - insert only letters
  City: <city>
  Insert the field using the pattern below:
    - insert only letters
  State: <state>
  Insert the field using the pattern below:
    - insert only letters
  Country: <country>
  User successfully created.

- **username**: Username is the identifier in the server.
- **first name**: The first name information.
- **last name**: The last name information.
- **password**: The password used to make changes in the server
- **password confirmation**: The password confirmation.
- **email**: Email to confirm the registration in the server.
- **phone**: Phone number information.This field is optional.
- **city**: City name information.This field is optional.
- **state**: State information.This field is optional.
- **country**: Country information. This field is optional.

After created you can't use your user yet.You need to confirm your
registration process in the email box passed.
After that you can upload yours NApps.

How to upload your NApp in the NApps repository
===============================================

First of all, to upload your napp you should have an active account in the
napps server. With an registered account you should execute the command below
inside the napp structure.

The command below will to compact your NApp and upload to the napps server.

.. code-block:: shell

  (kytos-environment)$ kytos napps upload
  Enter the username: <username>
  Enter the password for <username>: <password>
  SUCCESS: NApp <username>/my_first_napp uploaded.


If your NApp do not have a openapi.yml, the command executed will display the message:
`Do you have REST endpoints and wish to create an API skeleton in openapi.yml? (Y/n)`.
In this case if you input `y`, `Y` or `Enter` the file will be created,
otherwise the compacted NApp will be uploaded without this file.  Do not
worrying if your NApp do not have this file.

How the events works
====================

With the purpose of performing the communication between NApps in the `Kytos Project` 
any Napp can send or receive events.

Create Kytos Event
------------------

To create a new event you need to use the class KytosEvent and send that to
controller buffer. Below we have a python code to send a KytosEvent named
**<username>/napp_name.my_event** with a string as message in the content.

.. code-block:: python

    from kytos.core import KytosEvent, KytosNApp, log
    from kytos.core.events import KytosEvent # importing the KytosEvent

    class Main(KytosNapps): # KytosNapps Class

      # all KytosNapps methods
      # ...

      # method to send an event
      def send_event(self):
        # create an event
        event = KytosEvent(name='<username>/napp_name.my_event',
                           content={'message': 'My simple event'})

        # send an event to controller
        self.controller.buffers.app.put(event)

        # display that the event was sent.
        log.info('%s sent.', event.content['message'])

After created a method to send new events to Kytos you need to know how to
receive that event in your NApp.

Listen Kytos Event
------------------

In the Kytos core we have a decorator named **listen_to()** to call a function
when the kytos receive some specific event.  The parameter to **listen_to** is
a regex to filter the event by name.  For instance with you can receive all
events send by **<username>/napp_name** you can pass the string
**<username>/napp_name.***.

Below there is a function called when receive some event with the pattern
**<username>/napp_name.***.

.. code-block:: python

 from kytos.core import KytosEvent, KytosNApp, log
 from kytos.core.helpers import listen_to #import rest decorator method

 class Main(KytosNapps): # KytosNapps class

   # all KytosNapps methods
   # ...

   # Method to read all events named with the pattern below.
   @listen_to('<username>/napp_name.*')
   def receive_some_event(self, event):
      """Display a message from kytos event."""
      # display in the kytos console the event messsage.
      log.info(f"%s received.", event.content['message'])

Events that are generated by Kytos
==================================

In the Kytos project we have a list of events generated by kytos. You can read
the section :doc:`./listened_events` to know more about events generated by
kytos.

The kytos events are divided in some categories, below a list of all
categories is displayed.

.. toctree::
   :maxdepth: 3

   listened_events

Create your Meta-NApp
=====================

A Meta-Napp is a NApp that doesn't contain executable code, is used to specify dependencies of a given package 
and just installs and enables/disables a specific set of napps. 

To create your Meta-NApp, just like a common NApp, you need to use your napp-server name and insert some NApp
information. The difference is just the `meta` flag in the create command.

.. code-block:: shell

  (kytos-environment)$ kytos napps create --meta
  --------------------------------------------------------------
  Welcome to the bootstrap process of your NApp.
  --------------------------------------------------------------
  In order to answer both the username and the napp name,
  You must follow this naming rules:
  - name starts with a letter
  - name contains only letters, numbers or underscores
  - at least three characters
  --------------------------------------------------------------

  Please, insert your NApps Server username: <username>
  Please, insert your NApp name: <meta napp name>
  Please, insert a brief description for your NApp [optional]: <brief description>

  Congratulations! Your NApp have been bootstrapped!
  Now you can go to the directory {username}/{meta_napp_name} and begin to code your NApp.
  Have fun!

After that, a folder with `username` will be created and inside that we have
your Meta-NApp folder.

Understanding the Meta-NApp structure
-------------------------------------

The basic Meta-NApp structure is described below.

.. code-block:: shell

   <username>/
   ├── __init__.py
   └── <meta_napp_name>/
       ├── __init__.py
       ├── kytos.json
       ├── README.rst

- **kytos.json**: This is your Meta-NApp's main file, where the dependencies are defined.
- **README.rst**: Main description and information about your Meta-NApp, ensure that it includes a brief description of the dependencies

How to create a basic NApp dependency 
=====================================

First, you have to edit the `kytos.json` and set the napp_dependencies field with some napps. An example is displayed bellow.

.. code-block:: shell

  {
    ...
    "napp_dependencies": ["kytos/of_core"],
    ...
  }

Now, you have to install this Meta-NApp with the same command that was used to install a common NApp.

.. code-block:: shell

  $ kytos napps install username/meta_napp_name
  INFO    NApp username/meta_napp_name:
  INFO      Searching local NApp...
  INFO      Found and installed.
  INFO      Enabling...
  INFO  NApp enabled: username/meta_napp_name
  INFO      Enabled.
  INFO  Installing Dependencies:
  INFO    NApp kytos/of_core:
  INFO      Searching local NApp...
  INFO      Not found. Downloading from NApps Server...
  INFO      Downloaded and installed.
  INFO      Enabling...
  INFO  NApp enabled: kytos/of_core
  INFO      Enabled.

Finally, the Meta-Napp and its dependencies were installed. The Meta-Napp supports the same commands as a common Napp.

.. code-block:: shell

  $ kytos napps install/uninstall/enable/disable meta_napp_name