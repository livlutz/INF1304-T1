
#!/bin/bash
sudo docker ps -a

#TODO: ainda nao temos o consumer
sudo docker stop consumer
sudo docker rm consumer

./kill_broker.sh
