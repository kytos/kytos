
## docker-scripts

This folder contains information about docker-related scripts.

### `add-etc-hosts.sh`

`add-etc-hosts.sh` is meant for adding MongoDB container hostname in /etc/hosts, this is needed if you're not running `kytosd` in a container in the same docker network that mongo nodes are running. Make sure to run this script at least once when you're setting your development environment.

These entries are needed because `pymongo` client relies on the exact same hostnames that the replica set cluster was initially set up, so trying to use equivalent ones or localhost can result in unexpected behavior during nodes failover.

### `rs-init.sh`

`rs-init.sh` is meant for configuring the replica set nodes, which is automatically run when the `mongo-setup` is spinning up.
