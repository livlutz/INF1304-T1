#variaveis

PRODUCER_DIR = sensor
CONSUMER_DIR = consumer
FRONTEND_DIR = frontend

# Simulação completa com falhas aleatórias
all:
	make up
	@sleep 30
	make failure
	@sleep 20
	make recovery
	@sleep 30
	make failure
	@sleep 20
	make recovery
	@sleep 30
	make failure
	@sleep 20
	make recovery
	@sleep 30
	make failure
	@sleep 20
	make recovery
	@sleep 30
	make failure
	@sleep 20
	make recovery
	@sleep 30
	make failure
	@sleep 20
	make recovery
	make stop

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
	@nohup docker logs -f frontend > logs/frontend.log 2>&1 &
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
	@echo "=== Frontend Status ==="
	@echo "Aguardando frontend inicializar..."
	@sleep 5
	@docker logs frontend 2>/dev/null | head -10 || echo "Frontend ainda não iniciou completamente"

# Simula a queda aleatória de um broker ou consumer usando os scripts existentes
failure:
	@mkdir -p logs
	@RANDOM_SEED=$$(date +%s%N); \
	COMPONENT_TYPE=$$(($$RANDOM_SEED % 2)); \
	echo "Tipo de componente selecionado: $$COMPONENT_TYPE (0=broker, 1=consumer)"; \
	if [ $$COMPONENT_TYPE -eq 0 ]; then \
		BROKER_NUM=$$(($$RANDOM_SEED % 3 + 1)); \
		BROKER_NAME="kafka$$BROKER_NUM"; \
		echo "Derrubando broker: $$BROKER_NAME"; \
		echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Falha no broker $$BROKER_NAME usando kill_broker.sh" >> logs/simulation.log; \
		cd scripts && chmod +x kill_broker.sh && ./kill_broker.sh $$BROKER_NAME && cd ..; \
		echo "FAILED_COMPONENT=$$BROKER_NAME" > .simulation_state; \
		echo "COMPONENT_TYPE=BROKER" >> .simulation_state; \
	else \
		CONSUMER_NUM=$$(($$RANDOM_SEED % 3 + 1)); \
		CONSUMER_NAME="consumer$$CONSUMER_NUM"; \
		echo "Derrubando consumer: $$CONSUMER_NAME"; \
		echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Falha no consumer $$CONSUMER_NAME usando kill_consumer.sh" >> logs/simulation.log; \
		cd scripts && chmod +x kill_consumer.sh && ./kill_consumer.sh $$CONSUMER_NAME && cd ..; \
		echo "FAILED_COMPONENT=$$CONSUMER_NAME" > .simulation_state; \
		echo "COMPONENT_TYPE=CONSUMER" >> .simulation_state; \
	fi

# Decide se vai recuperar o componente ou deixar em falha
recovery:
	@if [ ! -f .simulation_state ]; then \
		echo "Erro: arquivo .simulation_state não encontrado. Execute 'make failure' primeiro."; \
		exit 1; \
	fi
	@RANDOM_SEED=$$(date +%s%N); \
	RECOVERY_DECISION=$$(($$RANDOM_SEED % 2)); \
	FAILED_COMPONENT=$$(grep FAILED_COMPONENT .simulation_state | cut -d'=' -f2); \
	COMPONENT_TYPE=$$(grep COMPONENT_TYPE .simulation_state | cut -d'=' -f2); \
	echo "$$RECOVERY_DECISION (0=manter falha, 1=recuperar)"; \
	if [ $$RECOVERY_DECISION -eq 0 ]; then \
		echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Decisão: $$FAILED_COMPONENT em falha" >> logs/simulation.log; \
	else \
		echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Decisão: Recuperando $$FAILED_COMPONENT" >> logs/simulation.log; \
		if [ "$$COMPONENT_TYPE" = "BROKER" ]; then \
			make recover-broker BROKER=$$FAILED_COMPONENT; \
		else \
			make recover-consumer CONSUMER=$$FAILED_COMPONENT; \
		fi; \
		echo "=== COMPONENTE $$FAILED_COMPONENT RECUPERADO ==="; \
	fi

# Recupera um broker específico
recover-broker:
	@echo "Recuperando broker: $(BROKER)"
	@docker start $(BROKER) || true
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Broker $(BROKER) recuperado" >> logs/simulation.log
	@sleep 5

# Recupera um consumer específico
recover-consumer:
	@echo "Recuperando consumer: $(CONSUMER)"
	@docker start $(CONSUMER) || true
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Consumer $(CONSUMER) recuperado com sucesso" >> logs/simulation.log
	@sleep 5

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
	@echo "Removendo arquivos de simulação..."
	rm -f .simulation_state || true
	@echo "Limpeza completa finalizada!"
	docker ps -a
