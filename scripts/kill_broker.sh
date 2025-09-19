#!/bin/bash
sudo docker ps -a

sudo docker stop kafka1
sudo docker stop kafka2
sudo docker stop kafka1

sudo docker rm kafka1
sudo docker rm kafka2
sudo docker rm kafka1

sudo docker ps -a