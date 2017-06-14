#########
Changelog
#########
All notable changes to the kytos project will be documented in this file.

[UNRELEASED] - Under development
********************************
Added
=====

Changed
=======

Deprecated
==========

Removed
=======

Fixed
=====

Security
========


[2017.1b3] - "bethania" beta3 - 2017-06-14
******************************************
Added
=====
- '/kytos/configuration/' endpoint to display kytos configuration.
- Add 'api_port' in kytos.conf. The default value is 8181.

Changed
=======
- OpenFlow specific code moved to NApps: Kytos now acts as an all-purpose controller.
- Log manager refactored
- Improvements in the web interface style, layout and usability
- Setup proccess now requires `pip`
- Kytos documentation now shows a dropdown with each release documentation.

Fixed
=====
- Web interface:
  - Fixed memory and CPU usage
- Now Kytos can register endpoints with different methods for the same URL.
- Now it's possible to start in debug mode using the command kytosd -D
- Several bug fixes
- Fix starting debug mode using the command kytos -D
- Removed sphinx warnings and improved documentation to have blueprints links.


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
    - Uses sendall() to make sure data is being correcly sent.
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
- Improved NApps management - uinstall, disable and unload
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
