#variaveis

PRODUCER_DIR = sensor
CONSUMER_DIR = consumer
FRONTEND_DIR = frontend

# Simulação completa com falhas aleatórias
all:
	make up
	@sleep 10
	@echo "Derrubando broker: kafka1"
	$(MAKE) kill-broker-kafka1
	@sleep 10
	$(MAKE) recover-broker-kafka1
	@sleep 10
	@echo "Derrubando broker: kafka2"
	$(MAKE) kill-broker-kafka2
	@sleep 10
	$(MAKE) recover-broker-kafka2
	@sleep 10
	@echo "Derrubando broker: kafka3"
	$(MAKE) kill-broker-kafka3
	@sleep 10
	$(MAKE) recover-broker-kafka3
	@sleep 10
	@echo "Derrubando consumer: consumer1"
	$(MAKE) kill-consumer-consumer1
	@sleep 10
	$(MAKE) recover-consumer-consumer1
	@sleep 10
	@echo "Derrubando consumer: consumer2"
	$(MAKE) kill-consumer-consumer2
	@sleep 10
	$(MAKE) recover-consumer-consumer2
	@sleep 10
	@echo "Derrubando consumer: consumer3"
	$(MAKE) kill-consumer-consumer3
	@sleep 10
	$(MAKE) recover-consumer-consumer3
	@sleep 10
	@echo "Simulação completa!"
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

# Recupera um broker específico
recover-broker:
	@echo "Recuperando broker: $(BROKER)"
	@docker start $(BROKER) || true
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Broker $(BROKER) recuperado" >> logs/$(BROKER).log
	@sleep 5
	@echo "Reiniciando captura de logs de $(BROKER)..."
	@nohup docker logs -f $(BROKER) >> logs/$(BROKER).log 2>&1 &

recover-broker-%:
	@$(MAKE) recover-broker BROKER=$*

# Recupera um consumer específico
recover-consumer:
	@echo "Recuperando consumer: $(CONSUMER)"
	@docker start $(CONSUMER) || true
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Consumer $(CONSUMER) recuperado com sucesso" >> logs/$(CONSUMER).log
	@sleep 5
	@echo "Reiniciando captura de logs de $(CONSUMER)..."
	@nohup docker logs -f $(CONSUMER) >> logs/$(CONSUMER).log 2>&1 &

recover-consumer-%:
	@$(MAKE) recover-consumer CONSUMER=$*

kill-consumer:
	@if [ -z "$(CONSUMER)" ]; then \
		echo "Usage: make kill-consumer CONSUMER=<name>  or make kill-consumer-<name>"; \
		exit 1; \
	fi
	@echo "Derrubando consumer: $(CONSUMER)"
	cd scripts && chmod +x kill_consumer.sh && ./kill_consumer.sh $(CONSUMER) && cd ..
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Consumer $(CONSUMER) derrubado com sucesso" >> logs/$(CONSUMER).log
	@sleep 5

# Pattern wrappers so user can call e.g. `make kill-consumer-consumer1` or `make kill-consumer CONSUMER=consumer1`
kill-consumer-%:
	@$(MAKE) kill-consumer CONSUMER=$*


kill-broker:
	@if [ -z "$(BROKER)" ]; then \
		echo "Usage: make kill-broker BROKER=<name>  or make kill-broker-<name>"; \
		exit 1; \
	fi
	@echo "Derrubando broker: $(BROKER)"
	cd scripts && chmod +x kill_broker.sh && ./kill_broker.sh $(BROKER) && cd ..
	@echo "$$(date '+%Y-%m-%d %H:%M:%S') [SIMULAÇÃO] Broker $(BROKER) derrubado com sucesso" >> logs/$(BROKER).log
	@sleep 5

# Pattern wrappers so user can call e.g. `make kill-broker-kafka1` or `make kill-broker BROKER=kafka1`
kill-broker-%:
	@$(MAKE) kill-broker BROKER=$*


# Limpa build dos containers
clean:
	@echo "Limpando partições antigas..."
	if docker inspect -f '{{.State.Running}}' kafka1 2>/dev/null | grep -q true; then \
		docker exec -it kafka1 /opt/kafka/bin/kafka-topics.sh \
		--delete --topic dados-sensores \
		--bootstrap-server kafka1:9092; \
	fi

	@echo "Parando e removendo containers..."
	make stop
	@echo "Removendo imagens Docker..."
	docker rmi -f inf1304-t1-sensor1 || true
	docker rmi -f inf1304-t1-sensor2 || true
	docker rmi -f inf1304-t1-sensor3 || true
	docker rmi -f inf1304-t1-consumer1 || true
	docker rmi -f inf1304-t1-consumer2 || true
	docker rmi -f inf1304-t1-consumer3 || true
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
