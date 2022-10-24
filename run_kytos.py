import cmd
import os


cmd = "sudo ./docker/scripts/add-etc-hosts.sh; export MONGO_USERNAME=alopalao; export MONGO_PASSWORD=123; docker-compose up -d; kytosd -f --database mongodb"
os.system(cmd)