
#variaveis

PRODUCER_DIR = sensor
CONSUMER_DIR = consumer

#TODO: ainda nao temos tudo para rodar tudo
all:
	make build
	make up
	make status

	#TODO: adicionar o make up depois de algum tempo

#Para e remove os containers
stop:
	@echo "Parando containers..."
	docker ps -a
	docker stop kafka1 || true
	docker stop kafka2 || true
	docker stop kafka3 || true
	docker stop sensor || true
	docker stop consumer || true
	docker rm sensor || true
	docker rm kafka1 || true
	docker rm kafka2 || true
	docker rm kafka3 || true
	docker rm consumer || true
	docker ps -a

# Constrói as imagens do docker do produtor e consumidor e kafkas
build:
	@echo "Criando os containers..."
	docker-compose build

# Sobe os containers e captura logs do consumidor, produtor e kafkas em seus respectivos arquivos
up:
	@echo "Subindo os containers..."
	docker-compose up -d
	@echo "Aguardando containers iniciarem..."
	@sleep 10
	@echo "Iniciando captura de logs..."
	@mkdir -p logs
	@nohup docker logs -f sensor > logs/producer.log 2>&1 &
	@nohup docker logs -f consumer > logs/consumer.log 2>&1 &
	@nohup docker logs -f kafka1 > logs/kafka1.log 2>&1 &
	@nohup docker logs -f kafka2 > logs/kafka2.log 2>&1 &
	@nohup docker logs -f kafka3 > logs/kafka3.log 2>&1 &
	@echo "Logs sendo salvos automaticamente em logs/"

# Lista os containers
status:
	@echo "Status dos containers:"
	docker ps -a

# Mostra logs em tempo real
logs:
	@echo "Mostrando logs dos containers (Ctrl+C para sair)..."
	docker-compose logs -f

# Logs separados
logs-producer:
	@echo "Mostrando logs do Producer..."
	docker-compose logs -f sensor

logs-kafka:
	@echo "Mostrando logs do Kafka..."
	docker-compose logs -f kafka

logs-consumer:
	@echo "Mostrando logs do Consumer..."
	docker-compose logs -f consumer

# Sobe o frontend
frontend:
	@echo "Iniciando frontend..."

# Limpa build do produtor e consumidor
clean:
	@echo "Parando e removendo containers..."
	make stop
	@echo "Removendo imagens Docker..."
	docker rmi -f inf1304-t1-sensor || true
	docker rmi -f inf1304-t1-consumer || true
	docker rmi -f apache/kafka:4.0.0 || true
	@echo "Removendo volumes Docker..."
	docker volume prune -f
	@echo "Limpando logs..."
	rm -rf logs/*.log || true
	@echo "Limpeza completa finalizada!"
	docker ps -a