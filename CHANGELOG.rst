#########
Changelog
#########
All notable changes to the kytos project will be documented in this file.

[UNRELEASED] - Under development
********************************
Added
=====
- `@rest` decorator can also be used before `@classmethod` or `@staticmethod`

Changed
=======
- Dependency installation/update for devs:
  `pip install -Ur requirements/dev.txt`. To use cloned kytos repos as
  dependencies, reinstall those repos with `pip install -e .` in the end.

Deprecated
==========

Removed
=======

Fixed
=====

Security
========


[2017.2b1] - "chico" beta1 - 2017-09-19
***************************************
Added
=====
- ``@rest`` decorator for REST API methods. Examples:

  - ``@rest('flow/<flow_id>')`` (only ``GET`` HTTP method by default);
  - ``@rest('flows/', methods=['GET', 'POST'])``.

- Guide for developers in documentation.

Changed
=======
- Whole documentation updated.
- API URLs renamed:

  - For NApps, the pattern is ``/api/<username>/<napp>/`` + what is defined in ``@rest`` decorator;
  - Core endpoints starts with ``/api/kytos/core/``. E.g. ``/kytos/config`` changed to ``/api/kytos/core/config``.

- Improved load/unload of NApps.
- Requirements files updated and restructured.
- Yala substitutes Pylama as the main linter checker.

Deprecated
==========
- Method ``register_rest_endpoint`` of ``Controller`` and ``APIServer`` in favor of ``@rest`` decorator.

Removed
=======

Fixed
=====
- Some bug fixes in tests.
- Several documentation fixes.
- Several bug fixes.

Security
========


[2017.1] - "bethania" - 2017-07-06
**********************************
Added
=====
- NAppDirListener to manage (load/unload) NApps when they are enabled or
  disabled using kytos-utils.

Changed
=======
- Improved connection management.
- Documentation updated and improved.
- Improved setup process.

Deprecated
==========

Removed
=======

Fixed
=====
- Some bug fixes.

Security
========


[2017.1b3] - "bethania" beta3 - 2017-06-16
******************************************
Added
=====
- Endpoint to display kytos configuration ('/kytos/config/').
- Setting to setup Kytos API Port on kytos.conf ('api_port' default to 8181).
- Documentation Blueprints tree.

Changed
=======
- OpenFlow specific code moved to NApps: Kytos now acts as an all-purpose
  controller.
- Log manager refactored
- Improvements in the web interface style, layout and usability
- Setup process now requires `pip`
- Kytos documentation now shows a dropdown with each release documentation.

Fixed
=====
- Web interface:
  - Fixed memory and CPU usage
- Now Kytos accepts to register different methods [POST, GET, etc] on the same
  endpoint.
- Now it's possible to start kytos in debug mode using `kytosd -D`.
- Removed documentation warnings.
- Several bug fixes


[2017.1b2] - "bethania" beta2 - 2017-05-05
******************************************
Added
=====
- Python bdist_wheel generation to make the install process via 'pip' easier
  and faster.
- Lockfile (PID-file) creation to prevent multiple instances running at the
  same time.
- Controller.restart method.
- kytos/tryfirst docker image was created and added to dockerhub.
- An improved console was added to execute python code when the controller is
  run in foreground.
- Continuous Integration with Code Quality Score and test coverage.
  (for the Python files in the project).
- Administration User Interface was moved to kytos, and it's accessible
  at port 8181 when kytos is running.
- Blueprints were moved to kytos/docs/blueprints folder.

Changed
=======
- Updated requirements.txt.
- Improvements in TCP Server:
    - Now makes sure the switch is fully connected before accepting data.
    - Makes sure the switch is still connected before sending any data.
    - Uses sendall() to make sure data is being correctly sent.
- NApps module was refactored.
- Improved 'clean' option of setup.py.
- Improved tests and style checks for developers.
- Kytos setup process improved, reading necessary metadata before installing.
- Kytos core package was refactored.
- Documentation updates.
- NApp information is now obtained from kytos.json when loading a NApp.
- Improved log management.

Deprecated
==========
- 'author' attribute, in the NApps context, was replaced by 'username' and
  will be removed in future releases.

Fixed
=====
- Friendly messages are now displayed when some exceptions are raised.
- Kytos configuration is now loaded properly from kytos.conf
- Several adjustments and bug fixes.


[2017.1b1] - "bethania" beta1 - 2017-03-24
******************************************
Added
=====
- Data gathering from switches (i.e. interface speed)
- REST endpoints (i.e. REST API status)
- Sphinxs documentation

Changed
=======
- Controller stop/start improvement
- Improved Controller's Rest API (using Flask)
- Connections, interfaces and switches management improvement
- Websocket to send logs to web interface
- Improved log management
- Corrections on setup and installation controller's code
- Improved NApps management - uninstall, disable and unload
- Improved controller's install and setup


[2016.1a1] - alpha1 - 2016-09-11
********************************
Added
=======
- Bootstrapped initial architechture
- Kytos Events managing buffers and handlers
- NApp handling (load/unload/start/shutdown)
- TCPServer and TCPHandler
- Added basic config class
