****************************
List REST Endpoints
****************************

This is a list of all REST endpoints in kytos/core and all the NApps.
You can test these endpoints using ``curl`` or a REST client like ``postman``.

Example request with ``curl``:

.. code:: shell

    $ curl http://127.0.0.1:8181/api/kytos/core/napps_installed/



Core REST Endpoints:
====================

Reload all NApps

.. code:: shell

    GET /api/kytos/core/reload/all/

Update Web UI, used with command ``kytos web update``.

.. code:: shell

    POST /api/kytos/core/web/update/

.. code:: shell

    POST /api/kytos/core/web/update/<version>/

Get a list of the installed NApps.

.. code:: shell

    GET /api/kytos/core/napps_installed/

Get enabled NApps.

.. code:: shell

    GET /api/kytos/core/napps_enabled/

Shutdown, used by stop_api_server.

.. code:: shell

    GET /api/kytos/core/shutdown/

Get kytos metadata:

.. code:: shell

    GET /api/kytos/core/metadata/


Get API Server status.

.. code:: shell

    GET /api/kytos/core/status/

Get config.

.. code:: shell

    GET /api/kytos/core/config/

Uninstall a NApp.

.. code:: shell

    GET /api/kytos/core/napps/<username>/<napp_name>/uninstall/

Get Metadata.

.. code:: shell

    GET /api/kytos/core/napps/<username>/<napp_name>/metadata/<key>/

Disable a NApp.

.. code:: shell

    GET /api/kytos/core/napps/<username>/<napp_name>/disable

Install a NApp.

.. code:: shell

    GET /api/kytos/core/napps/<username>/<napp_name>/install

Enable a NApp.

.. code:: shell

    GET /api/kytos/core/napps/<username>/<napp_name>/enable

Reload a NApp.

.. code:: shell

    GET /api/kytos/core/reload/<username>/<napp_name>/


**Auth Endpoints**

See the Auth documentation to get more information about this REST Endpoints.

Return a token if user and token are registered.

.. code:: shell

    GET /api/kytos/core/auth/login/


Create new user.

.. code:: shell

    POST /api/kytos/core/auth/users/


Retrieve all registered users.

.. code:: shell

    GET /api/kytos/core/auth/users/

Get details about a user.

.. code:: shell

    GET /api/kytos/core/auth/users/<uid>

Delete a user.

.. code:: shell

    DELETE /api/kytos/core/auth/users/<uid>

Update a user.

.. code:: shell

    PATCH /api/kytos/core/auth/users/<uid>

You can see a list of all the REST endpoints in the kytos console.
Run ``kytosd -f``, and run the code below on the kytos console:

.. code:: python

    urls = controller.api_server.app.url_map.iter_rules()
    routes = [(str(rule), rule.methods) for rule in urls]
    sorted(routes)


NApps' REST Endpoints
=====================

For more details on the NApps' REST endpoints, check the `NApp server
<https://napps.kytos.io/>`_.

**kytos/flow_manager**

See more details about flow_manager REST Endpoints in `kytos/flow_manager
<https://napps.kytos.io/kytos/flow_manager>`_.

.. code:: shell

    GET /api/kytos/flow_manager/v2/flows

.. code:: shell

    GET /api/kytos/flow_manager/v2/flows/<dpid>

.. code:: shell

    POST /api/kytos/flow_manager/v2/flows

.. code:: shell

    POST /api/kytos/flow_manager/v2/flows/<dpid>

.. code:: shell

    POST /api/kytos/flow_manager/v2/delete

.. code:: shell

    POST /api/kytos/flow_manager/v2/delete/<dpid>

**kytos/kronos**

See more details about kronos REST Endpoints in `kytos/kronos
<https://napps.kytos.io/kytos/kronos>`_.

.. code:: shell

    POST /api/kytos/kronos/v1/<namespace>/<value>

.. code:: shell

    POST /api/kytos/kronos/v1/<namespace>/<value>/<timestamp>

.. code:: shell

    DELETE /api/kytos/kronos/v1/<namespace>/

.. code:: shell

    DELETE /api/kytos/kronos/v1/<namespace>/start/<start>

.. code:: shell

    DELETE /api/kytos/kronos/v1/<namespace>/end/<end>

.. code:: shell

    DELETE /api/kytos/kronos/v1/<namespace>/<start>/<end>

.. code:: shell

    GET /api/kytos/kronos/v1/namespace/

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<start>/

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<end>/

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<start>/<end>

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/

.. code:: shell

    GET /api/kytos/kronos/v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/<group>

**kytos/maintenance**

See more details about maintenance REST Endpoints in `kytos/maintenance
<https://napps.kytos.io/kytos/maintenance>`_.

.. code:: shell

    GET /api/kytos/maintenance/

.. code:: shell

    GET /api/kytos/maintenance/<mw_id>

.. code:: shell

    POST /api/kytos/maintenance/

.. code:: shell

    PATCH /api/kytos/maintenance/<mw_id>

.. code:: shell

    DELETE /api/kytos/maintenance/<mw_id>

.. code:: shell

    PATCH /api/kytos/maintenance/<mw_id>/end

**kytos/mef_eline**

See more details about mef_eline REST Endpoints in `kytos/mef_eline
<https://napps.kytos.io/kytos/mef_eline>`_.

.. code:: shell

    GET /api/kytos/mef_eline/v2/evc/

.. code:: shell

    GET /api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: shell

    POST /api/kytos/mef_eline/v2/evc/

.. code:: shell

    PATCH /api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: shell

    DELETE /api/kytos/mef_eline/v2/evc/<circuit_id>

.. code:: shell

    GET /api/kytos/mef_eline/v2/evc/schedule

.. code:: shell

    POST /api/kytos/mef_eline/v2/evc/schedule/

.. code:: shell

    PATCH /api/kytos/mef_eline/v2/evc/schedule/<schedule_id>

.. code:: shell

    DELETE /api/kytos/mef_eline/v2/evc/schedule/<schedule_id>

**kytos/of_lldp**

See more details about of_lldp REST Endpoints in `kytos/of_lldp
<https://napps.kytos.io/kytos/of_lldp>`_.

.. code:: shell

    GET /api/kytos/of_lldp/v1/interfaces

.. code:: shell

    POST /api/kytos/of_lldp/v1/interfaces/disable

.. code:: shell

    POST /api/kytos/of_lldp/v1/interfaces/enable

.. code:: shell

    GET /api/kytos/of_lldp/v1/polling_time

.. code:: shell

    POST /api/kytos/of_lldp/v1/polling_time

.. code:: shell

    GET /api/kytos/of_lldp/v1/

**kytos/of_stats**

See more details about of_stats REST Endpoints in `kytos/of_stats
<https://napps.kytos.io/kytos/of_stats>`_.

.. code:: shell

    GET /api/kytos/of_stats/v1/<dpid>/ports/<int:port>

.. code:: shell

    GET /api/kytos/of_stats/v1/<dpid>/ports

.. code:: shell

    GET /api/kytos/of_stats/v1/<dpid>/flows/<flow_hash>

.. code:: shell

    GET /api/kytos/of_stats/v1/<dpid>/flows

.. code:: shell

    GET /api/kytos/of_stats/v1/<dpid>/ports/<int:port>/random

**kytos/pathfinder**

See more details about pathfinder REST Endpoints in `kytos/pathfinder
<https://napps.kytos.io/kytos/pathfinder>`_.

.. code:: shell

    POST /api/kytos/pathfinder/v2/

**kytos/status**

See more details about status REST Endpoints in `kytos/status
<https://napps.kytos.io/kytos/status>`_.

.. code:: shell


    GET /api/kytos/status/v1/

.. code:: shell

    GET /api/kytos/status/v1/napps

**kytos/storehouse**

See more details about storehouse REST Endpoints in `kytos/storehouse
<https://napps.kytos.io/kytos/storehouse>`_.

.. code:: shell

    POST /api/kytos/storehouse/v1/<namespace>

.. code:: shell

    POST /api/kytos/storehouse/v1/<namespace>/<name>

.. code:: shell

    POST /api/kytos/storehouse/v2/<namespace>

.. code:: shell

    POST /api/kytos/storehouse/v2/<namespace>/<box_id>

.. code:: shell

    GET /api/kytos/storehouse/v1/<namespace>

.. code:: shell

    PUT/PATCH /api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: shell

    GET /api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: shell

    DELETE /api/kytos/storehouse/v1/<namespace>/<box_id>

.. code:: shell

    GET /api/kytos/storehouse/v1/<namespace>/search_by/<filter_option>/<query>

.. code:: shell

    GET /api/kytos/storehouse/v1/backup/<namespace>/

.. code:: shell

    GET /api/kytos/storehouse/v1/backup/<namespace>/<box_id>

**kytos/topology**

See more details about topology REST Endpoints in `kytos/topology
<https://napps.kytos.io/kytos/topology>`_.

.. code:: shell

    GET /api/kytos/topology/v3/

.. code:: shell

    GET /api/kytos/topology/v3/restore

.. code:: shell

    GET /api/kytos/topology/v3/switches

.. code:: shell

    POST /api/kytos/topology/v3/switches/<dpid>/enable

.. code:: shell

    POST /api/kytos/topology/v3/switches/<dpid>/disable

.. code:: shell

    GET /api/kytos/topology/v3/switches/<dpid>/metadata


.. code:: shell

    POST /api/kytos/topology/v3/switches/<dpid>/metadata

.. code:: shell

    DELETE /api/kytos/topology/v3/switches/<dpid>/metadata/<key>

.. code:: shell

    GET /api/kytos/topology/v3/interfaces

.. code:: shell

    POST /api/kytos/topology/v3/interfaces/switch/<dpid>/enable

.. code:: shell

    POST /api/kytos/topology/v3/interfaces/<interface_enable_id>/enable

.. code:: shell

    POST /api/kytos/topology/v3/interfaces/switch/<dpid>/disable

.. code:: shell

    POST /api/kytos/topology/v3/interfaces/<interface_disable_id>/disable

.. code:: shell

    GET /api/kytos/topology/v3/interfaces/<interface_id>/metadata

.. code:: shell

    POST /api/kytos/topology/v3/interfaces/<interface_id>/metadata

.. code:: shell

    DELETE /api/kytos/topology/v3/interfaces/<interface_id>/metadata/<key>

.. code:: shell

    GET /api/kytos/topology/v3/links

.. code:: shell

    POST /api/kytos/topology/v3/links/<link_id>/enable

.. code:: shell

    POST /api/kytos/topology/v3/links/<link_id>/disable

.. code:: shell

    GET /api/kytos/topology/v3/links/<link_id>/metadata

.. code:: shell

    POST /api/kytos/topology/v3/links/<link_id>/metadata

.. code:: shell

    DELETE /api/kytos/topology/v3/links/<link_id>/metadata/<key>
