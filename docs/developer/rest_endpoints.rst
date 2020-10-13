****************************
List REST Endpoints
****************************

This is a list of all REST endpoints in kytos/core and all the NApps.
You can test these endpoints using ``curl`` or a REST client like ``postman``.

Example request with ``curl``:

.. code:: console

    curl http://0.0.0.0:8181/api/kytos/core/napps_installed/



Core REST Endpoints:
====================

Reload all NApps

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/reload/all/

Update Web UI, used with command ``kytos web update``.

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/core/web/update/

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/core/web/update/<version>/

Get a list of the installed NApps.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps_installed/

Get enabled NApps.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps_enabled/

Shutdown, used by stop_api_server.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/shutdown/

Get kytos metadata:

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/metadata/


Get API Server status.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/status/

Get config.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/config/

Uninstall a NApp.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps/<username>/<napp_name>/uninstall/

Get Metadata.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps/<username>/<napp_name>/metadata/<key>/

Disable a NApp.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps/<username>/<napp_name>/disable

Install a NApp.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps/<username>/<napp_name>/install

Enable a NApp.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/napps/<username>/<napp_name>/enable

Reload a NApp.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/reload/<username>/<napp_name>/


**Auth Endpoints**

See the Auth documentation to get more information about this REST Endpoints.

Return a token if user and token are registered.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/auth/login/


Create new user.

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/core/auth/users/


Retrieve all registered users.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/auth/users/

Get details about a user.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/core/auth/users/<uid>

Delete a user.

.. code:: console

    DELETE http://0.0.0.0:8181api/kytos/core/auth/users/<uid>

Update a user.

.. code:: console

    PATCH http://0.0.0.0:8181/api/kytos/core/auth/users/<uid>

You can see all core endpoints in kytos console.
Run ``kytosd -f``, and run the code bellow on the kytos console:

.. code:: python

    urls = controller.api_server.app.url_map.iter_rules()
    routes = [['%s' % rule, rule.methods] for rule in urls if 'kytos/core' in '%s' % rule]
    routes


NApps' REST Endpoints
=====================

For more details on the NApps' REST endpoints, check the `NApp server
<https://napps.kytos.io/>`_.

**kytos/flow_manager**

See more details about flow_manager REST Endpoints in `kytos/flow_manager
<https://napps.kytos.io/kytos/flow_manager>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/flow_manager/v2/flows

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/flow_manager/v2/flows/<dpid>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/flow_manager/v2/flows

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/flow_manager/v2/flows/<dpid>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/flow_manager/v2/delete

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/flow_manager/v2/delete/<dpid>

**kytos/kronos**

See more details about kronos REST Endpoints in `kytos/kronos
<https://napps.kytos.io/kytos/kronos>`_.

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<value>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<value>/<timestamp>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/start/<start>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/end/<end>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/<end>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/namespace/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<end>/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/<end>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/<group>

**kytos/maintenance**

See more details about maintenance REST Endpoints in `kytos/maintenance
<https://napps.kytos.io/kytos/maintenance>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/maintenance/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/maintenance/<mw_id>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/maintenance/

.. code:: console

    PATCH http://0.0.0.0:8181/api/kytos/maintenance/<mw_id>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/maintenance/<mw_id>

.. code:: console

    PATCH http://0.0.0.0:8181/api/kytos/maintenance/<mw_id>/end

**kytos/mef_eline**

See more details about mef_eline REST Endpoints in `kytos/mef_eline
<https://napps.kytos.io/kytos/mef_eline>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/

.. code:: console

    PATCH http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/schedule

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/schedule/

.. code:: console

    PATCH http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/schedule/<schedule_id>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/mef_eline/v2/evc/schedule/<schedule_id>

**kytos/of_lldp**

See more details about of_lldp REST Endpoints in `kytos/of_lldp
<https://napps.kytos.io/kytos/of_lldp>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_lldp/v1/interfaces

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/of_lldp/v1/interfaces/disable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/of_lldp/v1/interfaces/enable

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_lldp/v1/polling_time

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/of_lldp/v1/polling_time

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_lldp/v1/

**kytos/of_stats**

See more details about of_stats REST Endpoints in `kytos/of_stats
<https://napps.kytos.io/kytos/of_stats>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_stats/v1/<dpid>/ports/<int:port>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_stats/v1/<dpid>/ports

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_stats/v1/<dpid>/flows/<flow_hash>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_stats/v1/<dpid>/flows

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/of_stats/v1/<dpid>/ports/<int:port>/random

**kytos/pathfinder**

See more details about pathfinder REST Endpoints in `kytos/pathfinder
<https://napps.kytos.io/kytos/pathfinder>`_.

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/pathfinder/v2/

**kytos/status**

See more details about status REST Endpoints in `kytos/status
<https://napps.kytos.io/kytos/status>`_.

.. code:: console


    GET http://0.0.0.0:8181/api/kytos/status/v1/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/status/v1/napps

**kytos/storehouse**

See more details about storehouse REST Endpoints in `kytos/storehouse
<https://napps.kytos.io/kytos/storehouse>`_.

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>/<name>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/storehouse/v2/<namespace>

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/storehouse/v2/<namespace>/<box_id>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>

.. code:: console

    PUT/PATCH http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/storehouse/v1/<namespace>/search_by/<filter_option>/<query>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/storehouse/v1/backup/<namespace>/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/storehouse/v1/backup/<namespace>/<box_id>

**kytos/topology**

See more details about topology REST Endpoints in `kytos/topology
<https://napps.kytos.io/kytos/topology>`_.

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/restore

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/switches

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/switches/<dpid>/enable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/switches/<dpid>/disable

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/switches/<dpid>/metadata


.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/switches/<dpid>/metadata

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/topology/v3/switches/<dpid>/metadata/<key>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/interfaces

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/switch/<dpid>/enable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/<interface_enable_id>/enable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/switch/<dpid>/disable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/<interface_disable_id>/disable

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/<interface_id>/metadata

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/<interface_id>/metadata

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/topology/v3/interfaces/<interface_id>/metadata/<key>

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/links

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/links/<link_id>/enable

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/links/<link_id>/disable

.. code:: console

    GET http://0.0.0.0:8181/api/kytos/topology/v3/links/<link_id>/metadata

.. code:: console

    POST http://0.0.0.0:8181/api/kytos/topology/v3/links/<link_id>/metadata

.. code:: console

    DELETE http://0.0.0.0:8181/api/kytos/topology/v3/links/<link_id>/metadata/<key>
