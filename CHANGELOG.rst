#########
Changelog
#########
All notable changes to the kytos project will be documented in this file.

UNRELEASED - Under development
******************************
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


[2020.1b1] - "helena" beta1 - 2020-03-09
****************************************

Added
=====
- New unit tests for NApps:
    - `kytos/kronos`, coverage increased from 0% to 31%
    - `kytos/mef_eline`, coverage increased from 67% to 70%
    - `kytos/of_core`, coverage increased from 28% to 47%
- New blueprint: EP018 - Kytos testing pipeline and definitions.
- Added long description field for display in pypi.org.

Fixed
=====
- Fixed Scrutinizer coverage error.


[2019.2] - "gil" stable - 2019-12-20
*************************************

Changed
=======
- Increased token expiration time in auth module.


[2019.2rc1] - "gil" release candidate 1 - 2019-12-13
****************************************************

Added
=====
- New `etcd` backend for the Storehouse NApp (experimental)
- NApps Server now has e-mail verification and password reset for devs
- Added `python-openflow` unit test coverage section to Kytos Dev guide

Fixed
=====
- Fixed duplicated logs (#993)
- Fixed exception handling during NApp setup which could cause
  locks on kytosd shutdown (#1000)


[2019.2b3] - "gil" beta3 - 2019-12-06
**************************************

Added
=====
- New Authentication module - REST endpoints can now be protected
  using the `@authenticated` decorator.
- New unitests to the Authentication module.
- New `/metadata` REST endpoint to access package metadata.
  `kytos-utils` now uses this to look for version mismatches.

Changed
=======
- Blueprint EP018 - Updated endpoints to configure Authentication module.

Fixed
=====
- Fix kytos installation without virtual env (eg.: `sudo`).


[2019.2b2] - "gil" beta2 - 2019-10-18
**************************************

Added
=====
- New blueprint: EP018 - API Authentication.
- New blueprint: EP019 - Improvements on Statistics Metrics Collections.
- New blueprint: EP020 - Data and Settings Persistence.

Changed
=======
- Changed loggers to begin the hierarchy with "kytos."
- Modify the kytos developer mode to check the installation of configuration files.
- Blueprint EP016: Changed layout and improvement ideas.
- Blueprint EP017: More details on OpenFlow errors.


[2019.2b1] - "gil" beta1 - 2019-08-30
**************************************

Added
=====
 - `Interface` objects have a new boolean `lldp` attribute (default `True`).
   Other applications can look at this attribute to determine the LLDP behavior.

Changed
=======
 - Improved installation of dependencies - pinned versions for dependencies
   in the production and developer install modes.


[2019.1] - "fafa" stable - 2019-07-12
*************************************

 - This is the stable "fafa" version, based on the last beta pre-releases.
   No changes since the last rc1.

[2019.1rc1] - "fafa" rc1 - 2019-07-05
**************************************

Added
=====
- Added Makefile for packaging and uploading to PyPI
- Added string representations to `Switch` and `Interface`
- New unit test for TCP server exceptions

Changed
=======
- `pytest` is now the default tool for Kytos' unit tests
- Invalid command-line parameters emit warnings instead of halting kytosd start

Fixed
=====
- Fixed traceback when a switch loses connectivity


[2019.1b3] - "fafa" beta3 - 2019-06-17
**************************************

Added
=====
- Added REST API endpoints to manage NApps from remote applications
- New kytos/kronos NApp was released. This NApp will be responsible for
  handling time series data, with initial support for InfluxDB (EXPERIMENTAL).
  For now on, visit kytos/kronos changelog for updates.

Changed
=======
- kytos-utils is now decoupled from kytos core
- Changed default Openflow TCP port to 6653

Removed
=======
- Removed diraol's watchdog fork dependency

Fixed
=====
- Fixed kytos install from PyPI. Now dependencies are properly installed
- Fixed some grammar errors in documentation
- Fixed some linter issues

Security
========
- Changed some dependencies versions in order to fix security bugs

[2019.1b2] - "fafa" beta2 - 2019-05-03
**************************************

Added
=====
- Added MEF E-Line Link Up/Down definition blueprint
- Added documentation about using tox for unit tests

Fixed
=====
- Fixed bug when starting kytosd in background (#893)
- Fixed method get_next_available_tag under concurrent scenarios
- Fixed warning when compiling documentation

[2019.1b1] - "fafa" beta1 - 2019-03-15
**************************************

Added
=====
 - Added vlan_pool configuration on kytos.conf to support mef_eline. Now you
   can configure available vlans per interface
 - Added documentation to describe how to create a Meta Napp
 - Added documentation about Unit Tests

Changed
=======
 - Updated documentation to install python-openflow, kytos-utils and kytos in
   that order
 - Updated documentation to use pip3 instead pip
 - Link id is now based on endpoints hashes, instead of a random uuid. This
   fixes #875

Deprecated
==========

Removed
=======
 - Removed circular dependency of kytos-utils
 - Removed unnecessary comparison on interfaces if they are on the same switch

Fixed
=====
 - Fixed type declaration that broke sphinx-build
 - Fixed some linter issues
 - Fixed NApps settings reload. Now when you change a NApp settings the reload
   it will work

Security
========
 - Updated pyyaml and requests requirements versions, in order to fix
   vulnerabilities

[2018.2] - "ernesto" stable - 2018-12-30
****************************************

 - This is the stable "ernesto" version, based on the last beta pre-releases.
   No changes since the last rc1.

[2018.2rc1] - "ernesto" rc1 - 2018-12-21
****************************************

Added
=====

 - Support for meta-napps (EXPERIMENTAL)

[2018.2b3] - "ernesto" beta3 - 2018-12-14
*****************************************

Added
=====
 - Added support to reuse VLAN pool configurations on Interface
 - Added support for serialization of Link instances

Changed
=======
 - Improved test coverage
 - Blueprint EP015 (system tests) improved


[2018.2b2] - "ernesto" - 2018-10-15
***********************************

Changed
=======
 - Improved test coverage

Fixed
=====
 - Removed warnings for invalid port speed (fix #754)
 - Fixed port speed on web user interface
 - Update console to support IPython 7

[2018.2b1] - "ernesto" - 2018-09-06
**********************************
Added
=====
- Added methods to list all NApp listeners.

Changed
=======
- Blueprint EP12.rst updated in order to describe patch and delete operations.

Fixed
=====
- Fixed compatibility of Python 3.7
- Fixed some linter issues.

[2018.1] - "dalva" - 2018-07-19
*******************************
Fixed
=====
- Fixed napps pre-installed with default value.

[2018.1b3] - "dalva" beta3 - 2018-06-15
**************************************
Added
=====
- Added `reload/<username>/<napp_name>` endpoint to reload the NApp code
- Added `reload/all` endpoint to update the NApp code of all NApps
- Kytos console display the kytos version.
- Added method __repr__ on Napp class.
- Added method __eq__ on UNI class.
- UNI and TAG has method as_dict and `as_json`.
- Added method get_metadata `as_dict`.
- Added method to return all available vlans.
- Added method to return a specific interface by id.
- Added pre-install napps method.
- Added a better introduction of dev and admin guides.
- Better handling of active/enabled in Switch/Interface/Links entities.

Changed
=======
- Better handling of broken napps.
- Refactored `load_napps` method.
- Refactored `get_time` to return a datetime with UTC
- Migrated event handler threads to the main asyncio loop.
- Improve documentation to use kytos sphinx theme.

Fixed
=====
- Some documentation docstrings.

[2018.1b2] - "dalva" beta2 - 2018-4-20
**************************************
Added
=====
- Added  `str` and `repr` methods for KytosEvent and Connection classes to be
  easy to see logging and debugging information.
- Added `web/update/<version>/` endpoint to update Kytos Web Interface with a
  specific version.
- Added asyncio support in tcp server and controller. API Server, ipython,
  event handlers and event notifications are still running on separate threads.

Changed
=======
- Changed the components name provided by Kytos NApps to use the pattern:
  {username}-{nappname}-{component-section}-{filename}

Fixed
=====
- Fixed some docstrings and comments

[2018.1b1] - "dalva" beta1 - 2018-3-09
**************************************
Added
=====
- Added some new blueprints (EP012, EP013 and EP014)
- Now, we have few Entities inside the core (Switch, Interface and Link)
- Each Entity has metadata attribute (a dict)
- Added link attribute to the Interface class
- GenericEntity itself was added in this version also
- Added 'active' and 'enable' flags to GenericEntity (EP013)
- Added 'enable'/'disable' methods to child GenericEntity classes (EP013).
- Define available_tags according to link's interfaces.
- Endpoint ('/ui/all') to display a json with all napps ui components.
- Endpoint ('/ui/<path:filename>') to get file with a specific napp component.
- Now, kytosd is a python module, to make it easy to run with asyncio on the future;
- This pre-release implements EP013 and EP014 as discussed on our last Kytos Dev Meeting.

Changed
=======
- Moved Interface class to interface.py file
- Small refactor of Switch class.

Fixed
=====
- Some bug fixes

[2017.2] - "chico" - 2017-12-21
*******************************
Changed
=======
- Web User Interface totally updated, with new design and functionality:

  - Visual elements reorganized for better experience.
  - Better information about switches and interfaces in the network.
  - Extending interface functionalities became easier.


[2017.2b2] - "chico" beta2 - 2017-12-01
***************************************
Added
=====
- `@rest` decorator can also be used before `@classmethod` or `@staticmethod`.
- Remove napp endpoints when a napp is disabled.
- TCP Server OpenFlow known ports.
- Config to allow other personalized protocol names on TCP Server.
- NNI and UNI attributes to Interface class.
- Interfaces to Switch json output.
- Statistics information for switch interfaces.
- Allow cross origin resource sharing (CORS).
- Now supports speed information from OF 1.3 switchs.
- Generate Events for reconnected switches.

Changed
=======
- Dependency installation/update for devs:
  `pip install -Ur requirements/dev.txt`. To use cloned kytos repos as
  dependencies, reinstall those repos with `pip install -e .` in the end.
- Event name for a new switch. From `kytos/core.switches.new` to
  `kytos/core.switch.new`.

Removed
=======
- Flow class from flow module. It was moved to kytos/of_core NApp.

Fixed
=====
- Some bug fixes in tests.
- Several documentation fixes.
- Several bug fixes.
- Rest API prefix changed to "api/<username>/<nappname>".
- Now displays bandwidth values as bytes.
- Remove rest api endpoint when a NApp is disabled.
- Correctly update interface state and manage interfaces for switches.
- Some bug fixes.

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

Fixed
=====
- Some bug fixes in tests.
- Several documentation fixes.
- Several bug fixes.


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

Fixed
=====
- Some bug fixes.


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
