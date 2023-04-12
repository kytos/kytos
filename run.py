import os

command = dict()
command[1] = "sudo ./docker/scripts/add-etc-hosts.sh"
command[2] = "export MONGO_USERNAME=alopalao"
command[3] = "export MONGO_PASSWORD=alopalao"
command[4] = "docker compose up -d"
command[5] = "kytosd -f -E --database mongodb"

full = ""
print("******************************Commands that will execute******************************")

for i in range(1,6):
    print(command[i])
    full += command[i]+"; "
print("**************************************************************************************")
full = full[:-2]
os.system(full)