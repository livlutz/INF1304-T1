
#variaveis

PRODUCER_DIR = sensor

#TODO: ainda nao temos tudo para rodar tudo
all:

#TODO: falta parar e excluir o consumer
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

# Constrói as imagens
build:
	@echo "Criando os containers..."
	docker-compose build

# Sobe os containers
up:
	@echo "Subindo os containers..."
	docker-compose up -d

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

# Sobe o frontend
frontend:
	@echo "Iniciando frontend..."

# Limpa build do produtor e consumidor -> ta sem o consumidor
clean:
	stop
	@echo "Limpando builds..."
	docker ps -a