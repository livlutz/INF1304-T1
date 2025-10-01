#variaveis

PRODUCER_DIR = sensor
CONSUMER_DIR = consumer
FRONTEND_DIR = frontend

#TODO: ainda nao temos tudo para rodar tudo
#TODO: adicionar o make clean depois de algum tempo??
all:
	make build
	make up


#Para e remove os containers
stop:
	@echo "Parando containers..."
	docker ps -a
	docker stop kafka1 || true
	docker stop kafka2 || true
	docker stop kafka3 || true
	docker stop sensor1 || true
	docker stop sensor2 || true
	docker stop sensor3 || true
	docker stop consumer1 || true
	docker stop consumer2 || true
	docker stop consumer3 || true
	docker stop frontend || true
	docker rm sensor1 || true
	docker rm sensor2 || true
	docker rm sensor3 || true
	docker rm kafka1 || true
	docker rm kafka2 || true
	docker rm kafka3 || true
	docker rm consumer1 || true
	docker rm consumer2 || true
	docker rm consumer3 || true
	docker rm frontend || true
	docker ps -a

# Constrói as imagens do docker do produtor e consumidor e kafkas
build:
	@echo "Criando os containers..."
	docker-compose build

# Sobe os containers e captura logs do consumidor, produtor e kafkas em seus respectivos arquivos
up:
	make clean
	make build
	@echo "Subindo os containers..."
	docker-compose up -d
	@echo "Aguardando containers iniciarem..."
	@sleep 15
	@echo "Iniciando captura de logs..."
	@mkdir -p logs
	sudo chown -R $$USER:$$USER logs
	@nohup docker logs -f sensor1 > logs/sensor1.log 2>&1 &
	@nohup docker logs -f sensor2 > logs/sensor2.log 2>&1 &
	@nohup docker logs -f sensor3 > logs/sensor3.log 2>&1 &
	@nohup docker logs -f consumer1 > logs/consumer1.log 2>&1 &
	@nohup docker logs -f consumer2 > logs/consumer2.log 2>&1 &
	@nohup docker logs -f consumer3 > logs/consumer3.log 2>&1 &
	@nohup docker logs -f kafka1 > logs/kafka1.log 2>&1 &
	@nohup docker logs -f kafka2 > logs/kafka2.log 2>&1 &
	@nohup docker logs -f kafka3 > logs/kafka3.log 2>&1 &
	@echo "Logs sendo salvos automaticamente em logs/"
	make logs-frontend

# Lista os containers
status:
	@echo "Status dos containers:"
	docker ps -a

# Mostra logs em tempo real
logs:
	@echo "Mostrando logs dos containers (Ctrl+C para sair)..."
	docker-compose logs -f

# Logs separados
logs-sensors:
	@echo "Mostrando logs dos Sensores..."
	docker-compose logs -f sensor1 sensor2 sensor3

logs-kafka:
	@echo "Mostrando logs do Kafka..."
	docker-compose logs -f kafka1 kafka2 kafka3

logs-consumers:
	@echo "Mostrando logs dos Consumers..."
	docker-compose logs -f consumer1 consumer2 consumer3

logs-frontend:
	@echo "Mostrando logs do Frontend..."
	docker-compose logs -f frontend

# Limpa build dos containers
clean:
	@echo "Parando e removendo containers..."
	make stop
	@echo "Removendo imagens Docker..."
	docker rmi -f inf1304-t1-sensor || true
	docker rmi -f inf1304-t1-consumer || true
	docker rmi -f inf1304-t1-frontend || true
	docker rmi -f apache/kafka:4.0.0 || true
	@echo "Removendo volumes Docker..."
	docker volume prune -f
	@echo "Limpando logs..."
	sudo rm -rf logs/*.log || true
	sudo rm -rf logs/ || true
	@echo "Limpeza completa finalizada!"
	docker ps -a